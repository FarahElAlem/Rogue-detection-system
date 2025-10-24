"""
Flask web application for Rogue Device Detection System
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from functools import wraps
import json
from datetime import datetime, timedelta

from config import Config
from database import DatabaseManager
from detector import RogueDeviceDetector
from switch_connector import SwitchConnector


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
Config.load_from_file()
db = DatabaseManager(Config.DATABASE_PATH)
detector = RogueDeviceDetector(Config)

# Simple session-based authentication
USERS = {
    'admin': 'admin123'  # In production, use hashed passwords
}


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Main dashboard"""
    stats = detector.get_statistics()
    
    # Check if this is first run (no authorized devices)
    authorized_count = len(db.get_authorized_devices())
    show_first_run_help = (authorized_count == 0)
    
    return render_template('index.html', stats=stats, show_first_run_help=show_first_run_help)


@app.route('/devices')
@login_required
def devices_page():
    """Devices management page"""
    all_devices = db.get_all_devices()
    authorized_list = db.get_authorized_devices()
    return render_template('devices.html', devices=all_devices, authorized=authorized_list)


@app.route('/events')
@login_required
def events_page():
    """Security events page"""
    events = db.get_recent_events(limit=200)
    return render_template('events.html', events=events)


@app.route('/settings')
@login_required
def settings_page():
    """Settings page"""
    return render_template('settings.html', config=Config)


@app.route('/import-export')
@login_required
def import_export_page():
    """Import/Export page"""
    return render_template('import_export.html')


@app.route('/ports')
@login_required
def ports_page():
    """Port management page"""
    return render_template('ports.html')


@app.route('/quarantine')
@login_required
def quarantine_page():
    """Quarantine management page"""
    quarantined = db.get_quarantined_devices()
    return render_template('quarantine.html', quarantined_devices=quarantined)


# API Endpoints

@app.route('/api/scan', methods=['POST'])
@login_required
def api_scan():
    """Trigger a network scan"""
    results = detector.perform_scan()
    
    # Emit real-time update via WebSocket
    socketio.emit('scan_complete', results)
    
    return jsonify(results)


@app.route('/api/devices', methods=['GET'])
@login_required
def api_get_devices():
    """Get all devices"""
    devices = db.get_all_devices()
    return jsonify({'success': True, 'devices': devices})


@app.route('/api/devices/rogues', methods=['GET'])
@login_required
def api_get_rogues():
    """Get rogue devices only"""
    rogues = db.get_rogue_devices()
    return jsonify({'success': True, 'devices': rogues})  # Frontend expects 'devices' key


@app.route('/api/devices/<mac_address>/authorize', methods=['POST'])
@login_required
def api_authorize_device(mac_address):
    """Authorize a device"""
    data = request.get_json() or {}
    
    device_info = {
        'device_name': data.get('device_name', 'Unknown'),
        'device_type': data.get('device_type', 'Unknown'),
        'owner': data.get('owner', session.get('username', 'admin')),
        'department': data.get('department', 'IT'),
        'notes': data.get('notes', ''),
        'authorized_by': session.get('username', 'admin')
    }
    
    success = db.authorize_device(mac_address, device_info)
    
    if success:
        # If VLAN quarantine is enabled, restore device to proper VLAN
        if Config.ENABLE_VLAN_QUARANTINE:
            devices = db.get_all_devices()
            device = next((d for d in devices if d['mac_address'] == mac_address), None)
            
            if device and device.get('switch_port'):
                port = device['switch_port']
                
                # Get original VLAN or use default
                original_vlan = db.get_device_original_vlan(mac_address)
                target_vlan = original_vlan if original_vlan else Config.DEFAULT_AUTHORIZED_VLAN
                
                try:
                    with SwitchConnector(
                        host=Config.SWITCH_IP,
                        username=Config.SWITCH_USERNAME,
                        password=Config.SWITCH_PASSWORD,
                        secret=Config.SWITCH_ENABLE_PASSWORD
                    ) as switch:
                        # Move to authorized VLAN
                        switch.change_port_vlan(port, target_vlan)
                        
                        # Update database
                        db.restore_device_vlan(mac_address, target_vlan)
                        
                        db.log_event({
                            'event_type': 'VLAN_RESTORED',
                            'severity': 'INFO',
                            'mac_address': mac_address,
                            'switch_port': port,
                            'description': f'Authorized device restored to VLAN {target_vlan}',
                            'action_taken': f'Moved to VLAN {target_vlan}'
                        })
                except Exception as e:
                    print(f"Warning: Could not restore VLAN for {mac_address}: {e}")
        
        socketio.emit('device_authorized', {'mac_address': mac_address})
        return jsonify({'success': True, 'message': 'Device authorized successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to authorize device'}), 500


@app.route('/api/devices/<mac_address>/unauthorize', methods=['POST'])
@login_required
def api_unauthorize_device(mac_address):
    """Remove device from authorized list and immediately quarantine"""
    data = request.get_json() or {}
    immediate_quarantine = data.get('immediate_quarantine', True)  # Default: quarantine immediately
    
    # Get device info
    devices = db.get_all_devices()
    device = next((d for d in devices if d['mac_address'] == mac_address), None)
    
    if not device:
        return jsonify({'success': False, 'message': 'Device not found'}), 404
    
    # Step 1: Revoke authorization
    success = db.unauthorize_device(mac_address)
    
    if not success:
        return jsonify({'success': False, 'message': 'Failed to unauthorize device'}), 500
    
    # Step 2: Immediately quarantine if enabled
    if immediate_quarantine and Config.ENABLE_VLAN_QUARANTINE and device.get('switch_port'):
        port = device['switch_port']
        
        try:
            with SwitchConnector(
                host=Config.SWITCH_IP,
                username=Config.SWITCH_USERNAME,
                password=Config.SWITCH_PASSWORD,
                secret=Config.SWITCH_ENABLE_PASSWORD
            ) as switch:
                # Move to quarantine VLAN immediately
                success = switch.quarantine_port_vlan(port, Config.QUARANTINE_VLAN)
                
                if success:
                    # Update database
                    db.quarantine_device(mac_address, Config.QUARANTINE_VLAN, 'Authorization revoked')
                    
                    db.log_event({
                        'event_type': 'REVOKE_AND_QUARANTINE',
                        'severity': 'HIGH',
                        'mac_address': mac_address,
                        'switch_port': port,
                        'description': f'Authorization revoked and device immediately quarantined to VLAN {Config.QUARANTINE_VLAN}',
                        'action_taken': f'Moved to quarantine VLAN {Config.QUARANTINE_VLAN}'
                    })
                    
                    socketio.emit('device_quarantined', {'mac_address': mac_address, 'port': port, 'vlan': Config.QUARANTINE_VLAN})
                    
                    return jsonify({
                        'success': True, 
                        'message': f'Device authorization revoked and immediately quarantined to VLAN {Config.QUARANTINE_VLAN}',
                        'quarantined': True
                    })
        except Exception as e:
            # Quarantine failed, but authorization was revoked
            return jsonify({
                'success': True, 
                'message': f'Device unauthorized but quarantine failed: {str(e)}. Will be quarantined on next scan.',
                'quarantined': False
            })
    
    # No immediate quarantine - will be handled on next scan
    socketio.emit('device_unauthorized', {'mac_address': mac_address})
    return jsonify({
        'success': True, 
        'message': 'Device unauthorized successfully. Will be quarantined on next scan.',
        'quarantined': False
    })


@app.route('/api/devices/<mac_address>/isolate', methods=['POST'])
@login_required
def api_isolate_device(mac_address):
    """Isolate a rogue device (shutdown port)"""
    # Get device info to find port
    devices = db.get_all_devices()
    device = next((d for d in devices if d['mac_address'] == mac_address), None)
    
    if not device:
        return jsonify({'success': False, 'message': 'Device not found'}), 404
    
    port = device.get('switch_port')
    if not port:
        return jsonify({'success': False, 'message': 'Port information not available'}), 400
    
    success = detector.isolate_device(mac_address, port)
    
    if success:
        # Update port status in database
        db.update_port_status(port, 'shutdown', f'Isolated rogue device {mac_address}', session.get('username', 'admin'))
        
        socketio.emit('device_isolated', {'mac_address': mac_address, 'port': port})
        return jsonify({'success': True, 'message': f'Device isolated on port {port}'})
    else:
        return jsonify({'success': False, 'message': 'Failed to isolate device'}), 500


@app.route('/api/devices/<mac_address>/quarantine', methods=['POST'])
@login_required
def api_quarantine_device(mac_address):
    """Quarantine a device (move to quarantine VLAN or shutdown port)"""
    data = request.get_json() or {}
    reason = data.get('reason', 'Security violation')
    
    # Get device info
    devices = db.get_all_devices()
    device = next((d for d in devices if d['mac_address'] == mac_address), None)
    
    if not device:
        return jsonify({'success': False, 'message': 'Device not found'}), 404
    
    port = device.get('switch_port')
    if not port:
        return jsonify({'success': False, 'message': 'Port information not available'}), 400
    
    try:
        if Config.ENABLE_VLAN_QUARANTINE:
            # VLAN-based quarantine (preferred method)
            with SwitchConnector(
                host=Config.SWITCH_IP,
                username=Config.SWITCH_USERNAME,
                password=Config.SWITCH_PASSWORD
            ) as switch:
                # Move to quarantine VLAN
                success = switch.quarantine_port_vlan(port, Config.QUARANTINE_VLAN)
                
                if success:
                    # Update database
                    db.quarantine_device(mac_address, Config.QUARANTINE_VLAN, reason)
                    db.update_port_status(
                        port, 
                        'quarantine', 
                        f'Moved to VLAN {Config.QUARANTINE_VLAN}: {reason}', 
                        session.get('username', 'admin')
                    )
                    
                    db.log_event({
                        'event_type': 'VLAN_QUARANTINE',
                        'severity': 'HIGH',
                        'mac_address': mac_address,
                        'switch_port': port,
                        'description': f'Device moved to quarantine VLAN {Config.QUARANTINE_VLAN}: {reason}',
                        'action_taken': f'Moved to VLAN {Config.QUARANTINE_VLAN}'
                    })
                    
                    # Send email notification
                    detector.email_notifier.send_quarantine_alert(device, Config.QUARANTINE_VLAN)
                    
                    socketio.emit('device_quarantined', {'mac_address': mac_address, 'port': port, 'vlan': Config.QUARANTINE_VLAN})
                    return jsonify({
                        'success': True, 
                        'message': f'Device quarantined to VLAN {Config.QUARANTINE_VLAN} on port {port}',
                        'method': 'vlan'
                    })
                else:
                    return jsonify({'success': False, 'message': 'Failed to move to quarantine VLAN'}), 500
        else:
            # Port shutdown method (fallback)
            success = detector.isolate_device(mac_address, port)
            
            if success:
                db.quarantine_device(mac_address, 0, reason)
                db.update_port_status(port, 'quarantine', f'Port shutdown: {reason}', session.get('username', 'admin'))
                
                # Send email notification (port shutdown)
                detector.email_notifier.send_rogue_device_alert(device, f'Port {port} shut down - {reason}')
                
                socketio.emit('device_quarantined', {'mac_address': mac_address, 'port': port})
                return jsonify({
                    'success': True, 
                    'message': f'Device quarantined (port shutdown) on port {port}',
                    'method': 'shutdown'
                })
            else:
                return jsonify({'success': False, 'message': 'Failed to quarantine device'}), 500
                
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/ports/<path:port_name>/shutdown', methods=['POST'])
@login_required
def api_shutdown_port(port_name):
    """Shutdown a specific port"""
    # Debug: Print the received port name
    print(f"DEBUG: Received port_name: '{port_name}'")
    print(f"DEBUG: URL decoded: {request.view_args.get('port_name')}")
    
    data = request.get_json() or {}
    reason = data.get('reason', 'Manual shutdown')
    
    try:
        with SwitchConnector(
            host=Config.SWITCH_IP,
            username=Config.SWITCH_USERNAME,
            password=Config.SWITCH_PASSWORD
        ) as switch:
            success = switch.shutdown_port(port_name)
            
            if success:
                db.update_port_status(port_name, 'shutdown', reason, session.get('username', 'admin'))
                
                db.log_event({
                    'event_type': 'PORT_SHUTDOWN',
                    'severity': 'HIGH',
                    'switch_port': port_name,
                    'description': f'Port {port_name} manually shut down: {reason}',
                    'action_taken': 'Port disabled'
                })
                
                socketio.emit('port_shutdown', {'port': port_name})
                return jsonify({'success': True, 'message': f'Port {port_name} shut down successfully'})
            else:
                return jsonify({'success': False, 'message': 'Failed to shutdown port'})
    except Exception as e:
        print(f"Error in api_shutdown_port: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@app.route('/api/ports/<path:port_name>/enable', methods=['POST'])
@login_required
def api_enable_port(port_name):
    """Enable a specific port"""
    # Debug: Print the received port name
    print(f"DEBUG: Received port_name: '{port_name}'")
    print(f"DEBUG: URL decoded: {request.view_args.get('port_name')}")
    
    data = request.get_json() or {}
    reason = data.get('reason', 'Manual enable')
    
    try:
        with SwitchConnector(
            host=Config.SWITCH_IP,
            username=Config.SWITCH_USERNAME,
            password=Config.SWITCH_PASSWORD
        ) as switch:
            success = switch.enable_port(port_name)
            
            if success:
                db.update_port_status(port_name, 'enabled', reason, session.get('username', 'admin'))
                
                db.log_event({
                    'event_type': 'PORT_ENABLED',
                    'severity': 'INFO',
                    'switch_port': port_name,
                    'description': f'Port {port_name} manually enabled: {reason}',
                    'action_taken': 'Port enabled'
                })
                
                socketio.emit('port_enabled', {'port': port_name})
                return jsonify({'success': True, 'message': f'Port {port_name} enabled successfully'})
            else:
                return jsonify({'success': False, 'message': 'Failed to enable port'})
    except Exception as e:
        print(f"Error in api_enable_port: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@app.route('/api/ports/<path:port_name>/status', methods=['GET'])
@login_required
def api_get_port_status(port_name):
    """Get status of a specific port"""
    try:
        with SwitchConnector(
            host=Config.SWITCH_IP,
            username=Config.SWITCH_USERNAME,
            password=Config.SWITCH_PASSWORD
        ) as switch:
            details = switch.get_port_details(port_name)
            
            if details:
                # Also get database status
                db_status = db.get_port_status(port_name)
                
                return jsonify({
                    'success': True,
                    'port': port_name,
                    'switch_status': details,
                    'database_status': db_status
                })
            else:
                return jsonify({'success': False, 'message': 'Could not get port status'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/ports/status', methods=['GET'])
@login_required
def api_get_all_ports_status():
    """Get status of all ports"""
    try:
        with SwitchConnector(
            host=Config.SWITCH_IP,
            username=Config.SWITCH_USERNAME,
            password=Config.SWITCH_PASSWORD
        ) as switch:
            ports = switch.get_interface_status()
            db_ports = db.get_all_port_statuses()
            
            return jsonify({
                'success': True,
                'ports': ports if ports else [],
                'database_ports': db_ports if db_ports else []
            })
    except Exception as e:
        print(f"Error in api_get_all_ports_status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'message': f'Failed to get port status: {str(e)}',
            'ports': [],
            'database_ports': []
        }), 200  # Return 200 with error message instead of 500 to avoid HTML error page


@app.route('/api/ports/change-vlan', methods=['POST'])
@login_required
def api_change_port_vlan():
    """Change a port's VLAN"""
    data = request.get_json()
    port = data.get('port')
    vlan_id = data.get('vlan_id')
    reason = data.get('reason', 'VLAN changed via web interface')
    
    if not port or not vlan_id:
        return jsonify({'success': False, 'message': 'Port and VLAN ID are required'}), 400
    
    # Validate VLAN ID
    try:
        vlan_id = int(vlan_id)
        if vlan_id < 1 or vlan_id > 4094:
            return jsonify({'success': False, 'message': 'VLAN ID must be between 1 and 4094'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid VLAN ID'}), 400
    
    try:
        with SwitchConnector(
            host=Config.SWITCH_IP,
            username=Config.SWITCH_USERNAME,
            password=Config.SWITCH_PASSWORD,
            secret=Config.SWITCH_ENABLE_PASSWORD
        ) as switch:
            # Change the port VLAN
            success = switch.change_port_vlan(port, vlan_id)
            
            if success:
                # Log the event
                db.log_event({
                    'event_type': 'VLAN_CHANGED',
                    'severity': 'INFO',
                    'switch_port': port,
                    'description': f'Port {port} moved to VLAN {vlan_id}',
                    'action_taken': f'Changed to VLAN {vlan_id}: {reason}'
                })
                
                # Update port status in database
                db.update_port_status(
                    port_name=port,
                    admin_status='enabled',
#                    operational_status='up',
                    modified_by=session.get('username', 'admin'),
                    reason=reason
                )
                
                return jsonify({
                    'success': True, 
                    'message': f'Port {port} successfully moved to VLAN {vlan_id}'
                })
            else:
                return jsonify({
                    'success': False, 
                    'message': f'Failed to change VLAN on port {port}'
                }), 500
                
    except Exception as e:
        print(f"Error changing port VLAN: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/devices/<mac_address>/restore', methods=['POST'])
@login_required
def api_restore_device(mac_address):
    """Restore an isolated device"""
    devices = db.get_all_devices()
    device = next((d for d in devices if d['mac_address'] == mac_address), None)
    
    if not device:
        return jsonify({'success': False, 'message': 'Device not found'}), 404
    
    port = device.get('switch_port')
    if not port:
        return jsonify({'success': False, 'message': 'Port information not available'}), 400
    
    success = detector.restore_device(mac_address, port)
    
    if success:
        socketio.emit('device_restored', {'mac_address': mac_address, 'port': port})
        return jsonify({'success': True, 'message': f'Device restored on port {port}'})
    else:
        return jsonify({'success': False, 'message': 'Failed to restore device'}), 500


@app.route('/api/devices/<mac_address>/restore-vlan', methods=['POST'])
@login_required
def api_restore_device_vlan(mac_address):
    """Restore quarantined device to original VLAN without authorizing"""
    devices = db.get_all_devices()
    device = next((d for d in devices if d['mac_address'] == mac_address), None)
    
    if not device:
        return jsonify({'success': False, 'message': 'Device not found'}), 404
    
    port = device.get('switch_port')
    original_vlan = db.get_device_original_vlan(mac_address)
    
    if not port:
        return jsonify({'success': False, 'message': 'Port information not available'}), 400
    
    if not original_vlan:
        return jsonify({'success': False, 'message': 'Original VLAN not found'}), 400
    
    try:
        with SwitchConnector(
            host=Config.SWITCH_IP,
            username=Config.SWITCH_USERNAME,
            password=Config.SWITCH_PASSWORD
        ) as switch:
            success = switch.change_port_vlan(port, original_vlan)
            
            if success:
                db.restore_device_vlan(mac_address, original_vlan)
                db.log_event({
                    'event_type': 'VLAN_RESTORED',
                    'severity': 'INFO',
                    'mac_address': mac_address,
                    'switch_port': port,
                    'description': f'Device restored to original VLAN {original_vlan}',
                    'action_taken': f'Moved to VLAN {original_vlan}'
                })
                
                return jsonify({'success': True, 'message': f'Device restored to VLAN {original_vlan}'})
            else:
                return jsonify({'success': False, 'message': 'Failed to restore VLAN'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/devices/<mac_address>', methods=['DELETE'])
@login_required
def api_delete_device(mac_address):
    """Delete device from database"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM devices WHERE mac_address = ?', (mac_address,))
        conn.commit()
        conn.close()
        
        db.log_event({
            'event_type': 'DEVICE_DELETED',
            'severity': 'INFO',
            'mac_address': mac_address,
            'description': f'Device {mac_address} removed from database',
            'action_taken': 'Deleted from database'
        })
        
        return jsonify({'success': True, 'message': 'Device deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/quarantine/restore-all', methods=['POST'])
@login_required
def api_restore_all_quarantined():
    """Restore all quarantined devices to original VLANs"""
    quarantined = db.get_quarantined_devices()
    count = 0
    
    for device in quarantined:
        mac = device['mac_address']
        port = device.get('switch_port')
        original_vlan = db.get_device_original_vlan(mac)
        
        if port and original_vlan:
            try:
                with SwitchConnector(
                    host=Config.SWITCH_IP,
                    username=Config.SWITCH_USERNAME,
                    password=Config.SWITCH_PASSWORD
                ) as switch:
                    if switch.change_port_vlan(port, original_vlan):
                        db.restore_device_vlan(mac, original_vlan)
                        count += 1
            except Exception as e:
                print(f"Failed to restore {mac}: {e}")
    
    return jsonify({'success': True, 'count': count, 'message': f'Restored {count} devices'})


@app.route('/api/quarantine/clear-all', methods=['POST'])
@login_required
def api_clear_all_quarantined():
    """Remove all quarantined devices from database"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM devices WHERE status = "quarantined"')
        count = cursor.fetchone()['count']
        
        cursor.execute('DELETE FROM devices WHERE status = "quarantined"')
        conn.commit()
        conn.close()
        
        db.log_event({
            'event_type': 'QUARANTINE_CLEARED',
            'severity': 'HIGH',
            'description': f'All {count} quarantined devices removed from database',
            'action_taken': 'Bulk delete'
        })
        
        return jsonify({'success': True, 'count': count, 'message': f'Removed {count} devices'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/events', methods=['GET'])
@login_required
def api_get_events():
    """Get recent events"""
    limit = request.args.get('limit', 100, type=int)
    events = db.get_recent_events(limit=limit)
    return jsonify({'success': True, 'events': events})


@app.route('/api/statistics', methods=['GET'])
@login_required
def api_get_statistics():
    """Get system statistics"""
    stats = detector.get_statistics()
    return jsonify({'success': True, 'statistics': stats})


@app.route('/api/monitoring/start', methods=['POST'])
@login_required
def api_start_monitoring():
    """Start continuous monitoring"""
    detector.start_continuous_monitoring()
    return jsonify({'success': True, 'message': 'Monitoring started'})


@app.route('/api/monitoring/stop', methods=['POST'])
@login_required
def api_stop_monitoring():
    """Stop continuous monitoring"""
    detector.stop_continuous_monitoring()
    return jsonify({'success': True, 'message': 'Monitoring stopped'})


@app.route('/api/monitoring/status', methods=['GET'])
@login_required
def api_monitoring_status():
    """Get monitoring status"""
    return jsonify({
        'success': True,
        'is_running': detector.is_running,
        'latest_scan': detector.get_latest_results()
    })


@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def api_config():
    """Get or update configuration"""
    if request.method == 'POST':
        data = request.get_json()
        
        # Update configuration
        for key, value in data.items():
            if hasattr(Config, key.upper()):
                setattr(Config, key.upper(), value)
        
        # Save to file
        Config.save_to_file()
        
        return jsonify({'success': True, 'message': 'Configuration updated'})
    else:
        # Return current configuration
        config_dict = {
            'switch_ip': Config.SWITCH_IP,
            'switch_username': Config.SWITCH_USERNAME,
            'network_range': Config.NETWORK_RANGE,
            'scan_interval_seconds': Config.SCAN_INTERVAL_SECONDS,
            'auto_isolate_rogues': Config.AUTO_ISOLATE_ROGUES,
            'web_port': Config.WEB_PORT
        }
        return jsonify({'success': True, 'config': config_dict})


@app.route('/api/devices/import', methods=['POST'])
@login_required
def api_import_devices():
    """Import devices from JSON (for initial setup or backup restore)"""
    data = request.get_json()
    devices_list = data.get('devices', [])
    
    if not devices_list:
        return jsonify({'success': False, 'message': 'No devices provided'}), 400
    
    count = db.bulk_authorize_devices(devices_list)
    
    return jsonify({
        'success': True,
        'message': f'Imported {count} devices',
        'count': count
    })


@app.route('/api/devices/export', methods=['GET'])
@login_required
def api_export_devices():
    """Export all authorized devices (for backup)"""
    devices = db.get_authorized_devices()
    
    return jsonify({
        'success': True,
        'devices': devices,
        'count': len(devices)
    })


@app.route('/api/database/initialize', methods=['POST'])
@login_required
def api_initialize_database():
    """Initialize database with default authorized devices"""
    count = db.initialize_default_devices()
    
    return jsonify({
        'success': True,
        'message': f'Initialized with {count} default devices',
        'count': count
    })


@app.route('/api/database/reset', methods=['POST'])
@login_required
def api_reset_database():
    """Reset database (clear all data)"""
    data = request.get_json() or {}
    keep_authorized = data.get('keep_authorized', True)
    
    success = db.reset_database(keep_authorized=keep_authorized)
    
    if success:
        # Reset detector's latest scan results
        detector.latest_scan_results = {
            'timestamp': None,
            'total_devices': 0,
            'authorized': 0,
            'rogues': 0,
            'devices': []
        }
        
        return jsonify({
            'success': True,
            'message': f'Database reset successfully (authorized devices {"kept" if keep_authorized else "cleared"})'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to reset database'
        }), 500


# WebSocket events

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'message': 'Connected to Rogue Detection System'})


@socketio.on('request_update')
def handle_update_request():
    """Handle request for latest data"""
    stats = detector.get_statistics()
    latest_scan = detector.get_latest_results()
    emit('update', {'statistics': stats, 'latest_scan': latest_scan})


# Template filters

@app.route('/api/email/test', methods=['POST'])
@login_required
def api_test_email():
    """Test email configuration"""
    try:
        from email_notifier import EmailNotifier
        
        # Get email settings from request
        data = request.get_json() or {}
        print(f"Email test request data: {data}")
        
        # Validate required fields
        required_fields = ['smtp_server', 'smtp_username', 'smtp_password', 'email_from', 'email_to']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            })
        
        # Temporarily update config with provided settings
        original_config = {
            'smtp_server': Config.SMTP_SERVER,
            'smtp_port': Config.SMTP_PORT,
            'smtp_use_tls': Config.SMTP_USE_TLS,
            'smtp_username': Config.SMTP_USERNAME,
            'smtp_password': Config.SMTP_PASSWORD,
            'email_from': Config.EMAIL_FROM,
            'email_to': Config.EMAIL_TO,
            'enable_email_alerts': Config.ENABLE_EMAIL_ALERTS
        }
        
        # Update config with test settings
        Config.SMTP_SERVER = data.get('smtp_server', Config.SMTP_SERVER)
        Config.SMTP_PORT = int(data.get('smtp_port', Config.SMTP_PORT))
        Config.SMTP_USE_TLS = data.get('smtp_use_tls', Config.SMTP_USE_TLS)
        Config.SMTP_USERNAME = data.get('smtp_username', Config.SMTP_USERNAME)
        Config.SMTP_PASSWORD = data.get('smtp_password', Config.SMTP_PASSWORD)
        Config.EMAIL_FROM = data.get('email_from', Config.EMAIL_FROM)
        
        # Handle email_to (can be string or list)
        email_to = data.get('email_to', Config.EMAIL_TO)
        if isinstance(email_to, str):
            Config.EMAIL_TO = [email.strip() for email in email_to.split(',') if email.strip()]
        else:
            Config.EMAIL_TO = email_to if isinstance(email_to, list) else [email_to]
        
        Config.ENABLE_EMAIL_ALERTS = True
        
        print(f"Testing email with: {Config.SMTP_SERVER}:{Config.SMTP_PORT}")
        print(f"Username: {Config.SMTP_USERNAME}")
        print(f"To: {Config.EMAIL_TO}")
        
        # Create notifier and test
        notifier = EmailNotifier(Config)
        success = notifier.test_connection()
        
        # Restore original config
        Config.SMTP_SERVER = original_config['smtp_server']
        Config.SMTP_PORT = original_config['smtp_port']
        Config.SMTP_USE_TLS = original_config['smtp_use_tls']
        Config.SMTP_USERNAME = original_config['smtp_username']
        Config.SMTP_PASSWORD = original_config['smtp_password']
        Config.EMAIL_FROM = original_config['email_from']
        Config.EMAIL_TO = original_config['email_to']
        Config.ENABLE_EMAIL_ALERTS = original_config['enable_email_alerts']
        
        if success:
            return jsonify({'success': True, 'message': 'Test email sent successfully! Check your inbox.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send test email. Check SMTP settings and credentials.'})
            
    except Exception as e:
        print(f"Email test error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Email test failed: {str(e)}'})


@app.route('/api/settings/email', methods=['POST'])
@login_required
def api_update_email_settings():
    """Update email settings"""
    try:
        data = request.get_json()
        print(f"Received email settings data: {data}")
        
        # Update configuration
        if 'enable_email_alerts' in data:
            Config.ENABLE_EMAIL_ALERTS = data['enable_email_alerts']
            print(f"Set ENABLE_EMAIL_ALERTS to: {Config.ENABLE_EMAIL_ALERTS}")
        if 'smtp_server' in data:
            Config.SMTP_SERVER = data['smtp_server']
            print(f"Set SMTP_SERVER to: {Config.SMTP_SERVER}")
        if 'smtp_port' in data:
            Config.SMTP_PORT = int(data['smtp_port'])
            print(f"Set SMTP_PORT to: {Config.SMTP_PORT}")
        if 'smtp_use_tls' in data:
            Config.SMTP_USE_TLS = data['smtp_use_tls']
            print(f"Set SMTP_USE_TLS to: {Config.SMTP_USE_TLS}")
        if 'smtp_username' in data:
            Config.SMTP_USERNAME = data['smtp_username']
            print(f"Set SMTP_USERNAME to: {Config.SMTP_USERNAME}")
        if 'smtp_password' in data:
            Config.SMTP_PASSWORD = data['smtp_password']
            print(f"Set SMTP_PASSWORD to: {'*' * len(Config.SMTP_PASSWORD) if Config.SMTP_PASSWORD else 'None'}")
        if 'email_from' in data:
            Config.EMAIL_FROM = data['email_from']
            print(f"Set EMAIL_FROM to: {Config.EMAIL_FROM}")
        if 'email_to' in data:
            email_to = data['email_to']
            # Convert comma-separated string to list
            if isinstance(email_to, str):
                Config.EMAIL_TO = [e.strip() for e in email_to.split(',') if e.strip()]
            else:
                Config.EMAIL_TO = email_to
            print(f"Set EMAIL_TO to: {Config.EMAIL_TO}")
        if 'email_subject_prefix' in data:
            Config.EMAIL_SUBJECT_PREFIX = data['email_subject_prefix']
            print(f"Set EMAIL_SUBJECT_PREFIX to: {Config.EMAIL_SUBJECT_PREFIX}")
        
        # Save to file
        print("Saving configuration to file...")
        try:
            Config.save_to_file()
            print("Configuration saved successfully")
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return jsonify({'success': False, 'message': f'Failed to save configuration: {str(e)}'}), 500
        
        # Reload configuration from file to ensure it's properly loaded
        print("Reloading configuration from file...")
        try:
            Config.load_from_file()
            print("Configuration reloaded from file")
        except Exception as e:
            print(f"Error reloading configuration: {e}")
            return jsonify({'success': False, 'message': f'Failed to reload configuration: {str(e)}'}), 500
        
        # Verify the save worked
        print(f"Verification - ENABLE_EMAIL_ALERTS: {Config.ENABLE_EMAIL_ALERTS}")
        print(f"Verification - SMTP_USERNAME: {Config.SMTP_USERNAME}")
        print(f"Verification - EMAIL_TO: {Config.EMAIL_TO}")
        
        # Reinitialize detector's email notifier
        print("Reinitializing email notifier...")
        try:
            from email_notifier import EmailNotifier
            detector.email_notifier = EmailNotifier(Config)
            print("Email notifier reinitialized successfully")
        except Exception as e:
            print(f"Error reinitializing email notifier: {e}")
            return jsonify({'success': False, 'message': f'Failed to reinitialize email notifier: {str(e)}'}), 500
        
        return jsonify({'success': True, 'message': 'Email settings updated successfully'})
        
    except Exception as e:
        print(f"Error updating email settings: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


# Template Filters

@app.template_filter('datetime')
def format_datetime(value):
    """Format datetime for display"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    return value


@app.template_filter('severity_color')
def severity_color(severity):
    """Get Bootstrap color class for severity"""
    colors = {
        'CRITICAL': 'danger',
        'HIGH': 'warning',
        'MEDIUM': 'info',
        'LOW': 'secondary',
        'INFO': 'primary'
    }
    return colors.get(severity, 'secondary')


@app.template_filter('status_badge')
def status_badge(status):
    """Get Bootstrap badge class for status"""
    badges = {
        'active': 'success',
        'isolated': 'danger',
        'unknown': 'secondary'
    }
    return badges.get(status, 'secondary')


# Debug route removed - using <path:port_name> now handles slashes correctly

if __name__ == '__main__':
    # Start continuous monitoring on startup
    detector.start_continuous_monitoring()
    
    # Run Flask app
    socketio.run(
        app,
        host=Config.WEB_HOST,
        port=Config.WEB_PORT,
        debug=False,
        allow_unsafe_werkzeug=True
    )

