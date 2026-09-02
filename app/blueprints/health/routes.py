from datetime import datetime, timezone
from flask import jsonify, request, current_app
from sqlalchemy import text
from app import db, limiter
from . import health_bp

@health_bp.route('/', methods=['GET'])
@limiter.exempt
def health_check():
    """Endpoint de health check completo com status do banco de dados"""
    # Verificar token de segurança opcional
    expected_token = current_app.config.get('HEALTH_CHECK_TOKEN')
    if expected_token and expected_token != 'secure-token':
        token = request.headers.get('X-Health-Token') or request.args.get('token')
        if token != expected_token:
            return jsonify({'status': 'unhealthy', 'reason': 'Unauthorized'}), 401

    # Verificar status do banco de dados
    db_status = 'connected'
    try:
        db.session.execute(text('SELECT 1'))
    except Exception as e:
        db_status = f'disconnected: {str(e)}'
    
    status_code = 200 if db_status == 'connected' else 503
    
    response = {
        'status': 'healthy' if db_status == 'connected' else 'unhealthy',
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'version': current_app.config.get('VERSION', '1.2.0'),
        'database': db_status,
        'uptime': current_app.config.get('START_TIME', 'unknown'),
        'environment': current_app.config.get('ENV', 'development')
    }
    
    return jsonify(response), status_code

@health_bp.route('/ready', methods=['GET'])
@limiter.exempt
def readiness_check():
    """Verifica se a aplicação está pronta para receber tráfego"""
    # Pode ser expandido para checar outras dependências como Redis ou APIs externas
    return jsonify({'ready': True}), 200

@health_bp.route('/live', methods=['GET'])
@limiter.exempt
def liveness_check():
    """Verifica se a aplicação está viva para orquestradores como Kubernetes"""
    return jsonify({'alive': True}), 200
