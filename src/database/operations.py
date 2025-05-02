"""
G3r4ki Database Operations

This module provides utility functions for interacting with the database.
"""

import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from . import get_session
from .models import (
    Operation, Agent, Activity, File, C2Server, 
    Credential, Configuration
)

# Configure logging
logger = logging.getLogger("g3r4ki.database.operations")

#
# Operation Management
#

def create_operation(name: str, operation_type: str, description: Optional[str] = None,
                   operator: Optional[str] = None, target_scope: Optional[str] = None) -> Optional[int]:
    """
    Create a new offensive operation.
    
    Args:
        name: Name of the operation
        operation_type: Type of operation (rat, keylogger, c2, etc.)
        description: Optional description
        operator: Optional operator name
        target_scope: Optional target scope information (JSON string)
        
    Returns:
        Operation ID if successful, None otherwise
    """
    try:
        session = get_session()
        if not session:
            return None
        
        operation = Operation(
            name=name,
            description=description,
            operator=operator,
            operation_type=operation_type,
            target_scope=target_scope,
            start_time=datetime.datetime.utcnow(),
            status='created'
        )
        
        session.add(operation)
        session.commit()
        
        operation_id = operation.id
        session.close()
        
        logger.info(f"Created operation '{name}' with ID {operation_id}")
        return operation_id
    
    except Exception as e:
        logger.error(f"Error creating operation: {e}")
        if session:
            session.rollback()
            session.close()
        return None

def get_operation(operation_id: int) -> Optional[Dict[str, Any]]:
    """
    Get operation details by ID.
    
    Args:
        operation_id: ID of the operation
        
    Returns:
        Dictionary with operation details or None if not found
    """
    try:
        session = get_session()
        if not session:
            return None
        
        operation = session.query(Operation).filter(Operation.id == operation_id).first()
        
        if not operation:
            session.close()
            return None
        
        result = {
            'id': operation.id,
            'name': operation.name,
            'description': operation.description,
            'start_time': operation.start_time,
            'end_time': operation.end_time,
            'status': operation.status,
            'operator': operation.operator,
            'operation_type': operation.operation_type,
            'target_scope': operation.target_scope,
            'notes': operation.notes
        }
        
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error getting operation: {e}")
        if session:
            session.close()
        return None

def list_operations(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List operations.
    
    Args:
        limit: Maximum number of operations to return
        offset: Offset for pagination
        
    Returns:
        List of operations
    """
    try:
        session = get_session()
        if not session:
            return []
        
        operations = session.query(Operation).order_by(Operation.start_time.desc()).limit(limit).offset(offset).all()
        
        result = []
        for op in operations:
            result.append({
                'id': op.id,
                'name': op.name,
                'description': op.description,
                'start_time': op.start_time,
                'end_time': op.end_time,
                'status': op.status,
                'operator': op.operator,
                'operation_type': op.operation_type
            })
        
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error listing operations: {e}")
        if session:
            session.close()
        return []

def update_operation_status(operation_id: int, status: str, end_time: Optional[bool] = False) -> bool:
    """
    Update operation status.
    
    Args:
        operation_id: ID of the operation
        status: New status
        end_time: Set end time if True
        
    Returns:
        True if successful, False otherwise
    """
    try:
        session = get_session()
        if not session:
            return False
        
        operation = session.query(Operation).filter(Operation.id == operation_id).first()
        
        if not operation:
            session.close()
            return False
        
        operation.status = status
        if end_time:
            operation.end_time = datetime.datetime.utcnow()
        
        session.commit()
        session.close()
        
        logger.info(f"Updated operation {operation_id} status to '{status}'")
        return True
    
    except Exception as e:
        logger.error(f"Error updating operation status: {e}")
        if session:
            session.rollback()
            session.close()
        return False

#
# Agent Management
#

def register_agent(operation_id: int, agent_id: str, platform: str, agent_type: str,
                 hostname: Optional[str] = None, username: Optional[str] = None,
                 ip_address: Optional[str] = None, 
                 capabilities: Optional[List[str]] = None) -> Optional[int]:
    """
    Register a new agent.
    
    Args:
        operation_id: ID of the operation
        agent_id: Unique identifier for the agent
        platform: Platform (windows, linux, macos, android, ios)
        agent_type: Type of agent (rat, keylogger, c2_client, etc.)
        hostname: Optional hostname
        username: Optional username
        ip_address: Optional IP address
        capabilities: Optional list of capabilities
        
    Returns:
        Agent ID if successful, None otherwise
    """
    try:
        session = get_session()
        if not session:
            return None
        
        # Check if operation exists
        operation = session.query(Operation).filter(Operation.id == operation_id).first()
        if not operation:
            session.close()
            logger.error(f"Operation {operation_id} not found")
            return None
        
        # Check if agent already exists
        existing_agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
        if existing_agent:
            # Update existing agent
            existing_agent.operation_id = operation_id
            existing_agent.platform = platform
            existing_agent.agent_type = agent_type
            existing_agent.hostname = hostname
            existing_agent.username = username
            existing_agent.ip_address = ip_address
            existing_agent.check_in_time = datetime.datetime.utcnow()
            existing_agent.last_active = datetime.datetime.utcnow()
            existing_agent.status = 'active'
            
            if capabilities:
                existing_agent.capabilities = json.dumps(capabilities)
            
            session.commit()
            agent_db_id = existing_agent.id
            
            logger.info(f"Updated existing agent {agent_id} (ID: {agent_db_id})")
        else:
            # Create new agent
            agent = Agent(
                agent_id=agent_id,
                operation_id=operation_id,
                platform=platform,
                agent_type=agent_type,
                hostname=hostname,
                username=username,
                ip_address=ip_address,
                check_in_time=datetime.datetime.utcnow(),
                last_active=datetime.datetime.utcnow(),
                status='active',
                capabilities=json.dumps(capabilities) if capabilities else None
            )
            
            session.add(agent)
            session.commit()
            agent_db_id = agent.id
            
            logger.info(f"Registered new agent {agent_id} (ID: {agent_db_id})")
        
        session.close()
        return agent_db_id
    
    except Exception as e:
        logger.error(f"Error registering agent: {e}")
        if session:
            session.rollback()
            session.close()
        return None

def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    """
    Get agent details by agent ID.
    
    Args:
        agent_id: Agent ID
        
    Returns:
        Dictionary with agent details or None if not found
    """
    try:
        session = get_session()
        if not session:
            return None
        
        agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
        
        if not agent:
            session.close()
            return None
        
        result = {
            'id': agent.id,
            'agent_id': agent.agent_id,
            'operation_id': agent.operation_id,
            'name': agent.name,
            'platform': agent.platform,
            'agent_type': agent.agent_type,
            'ip_address': agent.ip_address,
            'hostname': agent.hostname,
            'username': agent.username,
            'check_in_time': agent.check_in_time,
            'last_active': agent.last_active,
            'status': agent.status,
            'capabilities': json.loads(agent.capabilities) if agent.capabilities else None,
            'configuration': json.loads(agent.configuration) if agent.configuration else None
        }
        
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        if session:
            session.close()
        return None

def list_agents(operation_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List agents.
    
    Args:
        operation_id: Optional operation ID to filter by
        limit: Maximum number of agents to return
        offset: Offset for pagination
        
    Returns:
        List of agents
    """
    try:
        session = get_session()
        if not session:
            return []
        
        query = session.query(Agent)
        
        if operation_id is not None:
            query = query.filter(Agent.operation_id == operation_id)
        
        agents = query.order_by(Agent.last_active.desc()).limit(limit).offset(offset).all()
        
        result = []
        for agent in agents:
            result.append({
                'id': agent.id,
                'agent_id': agent.agent_id,
                'operation_id': agent.operation_id,
                'name': agent.name,
                'platform': agent.platform,
                'agent_type': agent.agent_type,
                'ip_address': agent.ip_address,
                'hostname': agent.hostname,
                'username': agent.username,
                'check_in_time': agent.check_in_time,
                'last_active': agent.last_active,
                'status': agent.status
            })
        
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        if session:
            session.close()
        return []

def update_agent_status(agent_id: str, status: str) -> bool:
    """
    Update agent status.
    
    Args:
        agent_id: Agent ID
        status: New status
        
    Returns:
        True if successful, False otherwise
    """
    try:
        session = get_session()
        if not session:
            return False
        
        agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
        
        if not agent:
            session.close()
            return False
        
        agent.status = status
        agent.last_active = datetime.datetime.utcnow()
        
        session.commit()
        session.close()
        
        logger.info(f"Updated agent {agent_id} status to '{status}'")
        return True
    
    except Exception as e:
        logger.error(f"Error updating agent status: {e}")
        if session:
            session.rollback()
            session.close()
        return False

#
# Activity Logging
#

def log_activity(operation_id: int, activity_type: str, agent_id: Optional[str] = None,
               command: Optional[str] = None, output: Optional[str] = None,
               status: str = 'success', metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
    """
    Log an activity.
    
    Args:
        operation_id: ID of the operation
        activity_type: Type of activity
        agent_id: Optional agent ID
        command: Optional command or action
        output: Optional output or result
        status: Status of the activity (success, failed, error)
        metadata: Optional metadata dictionary
        
    Returns:
        Activity ID if successful, None otherwise
    """
    try:
        session = get_session()
        if not session:
            return None
        
        # Resolve agent database ID if agent_id is provided
        agent_db_id = None
        if agent_id:
            agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
            if agent:
                agent_db_id = agent.id
                
                # Update agent last active time
                agent.last_active = datetime.datetime.utcnow()
        
        # Create activity record
        activity = Activity(
            operation_id=operation_id,
            agent_id=agent_db_id,
            activity_type=activity_type,
            command=command,
            output=output,
            status=status,
            meta_data=json.dumps(metadata) if metadata else None
        )
        
        session.add(activity)
        session.commit()
        
        activity_id = activity.id
        session.close()
        
        logger.info(f"Logged {activity_type} activity (ID: {activity_id})")
        return activity_id
    
    except Exception as e:
        logger.error(f"Error logging activity: {e}")
        if session:
            session.rollback()
            session.close()
        return None

def get_activities(operation_id: int, agent_id: Optional[str] = None, 
                 activity_type: Optional[str] = None,
                 limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get activities for an operation.
    
    Args:
        operation_id: ID of the operation
        agent_id: Optional agent ID to filter by
        activity_type: Optional activity type to filter by
        limit: Maximum number of activities to return
        offset: Offset for pagination
        
    Returns:
        List of activities
    """
    try:
        session = get_session()
        if not session:
            return []
        
        query = session.query(Activity).filter(Activity.operation_id == operation_id)
        
        if agent_id:
            # First, get the agent's database ID
            agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
            if agent:
                query = query.filter(Activity.agent_id == agent.id)
        
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
        
        activities = query.order_by(Activity.timestamp.desc()).limit(limit).offset(offset).all()
        
        result = []
        for activity in activities:
            result.append({
                'id': activity.id,
                'operation_id': activity.operation_id,
                'agent_id': activity.agent_id,
                'timestamp': activity.timestamp,
                'activity_type': activity.activity_type,
                'command': activity.command,
                'output': activity.output,
                'status': activity.status,
                'metadata': json.loads(activity.meta_data) if activity.meta_data else None
            })
        
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error getting activities: {e}")
        if session:
            session.close()
        return []

#
# File Management
#

def register_file(agent_id: str, filename: str, file_type: str, file_path: Optional[str] = None,
                file_size: Optional[int] = None, content_type: Optional[str] = None,
                stored_path: Optional[str] = None, content_small: Optional[bytes] = None,
                metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
    """
    Register a file.
    
    Args:
        agent_id: Agent ID
        filename: Name of the file
        file_type: Type of file (keylog, screenshot, download, upload, etc.)
        file_path: Optional path of the file on the target system
        file_size: Optional size of the file in bytes
        content_type: Optional MIME type
        stored_path: Optional path where the file is stored locally
        content_small: Optional file content for small files
        metadata: Optional metadata dictionary
        
    Returns:
        File ID if successful, None otherwise
    """
    try:
        session = get_session()
        if not session:
            return None
        
        # Resolve agent database ID
        agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            session.close()
            logger.error(f"Agent {agent_id} not found")
            return None
        
        # Create file record
        file_record = File(
            agent_id=agent.id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            content_type=content_type,
            stored_path=stored_path,
            content_small=content_small,
            meta_data=json.dumps(metadata) if metadata else None
        )
        
        session.add(file_record)
        session.commit()
        
        file_id = file_record.id
        session.close()
        
        logger.info(f"Registered file {filename} (ID: {file_id})")
        return file_id
    
    except Exception as e:
        logger.error(f"Error registering file: {e}")
        if session:
            session.rollback()
            session.close()
        return None

def get_files(agent_id: Optional[str] = None, file_type: Optional[str] = None,
            limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get files.
    
    Args:
        agent_id: Optional agent ID to filter by
        file_type: Optional file type to filter by
        limit: Maximum number of files to return
        offset: Offset for pagination
        
    Returns:
        List of files
    """
    try:
        session = get_session()
        if not session:
            return []
        
        query = session.query(File)
        
        if agent_id:
            # First, get the agent's database ID
            agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
            if agent:
                query = query.filter(File.agent_id == agent.id)
        
        if file_type:
            query = query.filter(File.file_type == file_type)
        
        files = query.order_by(File.upload_time.desc()).limit(limit).offset(offset).all()
        
        result = []
        for file_record in files:
            result.append({
                'id': file_record.id,
                'agent_id': file_record.agent_id,
                'filename': file_record.filename,
                'file_path': file_record.file_path,
                'file_type': file_record.file_type,
                'file_size': file_record.file_size,
                'content_type': file_record.content_type,
                'upload_time': file_record.upload_time,
                'md5_hash': file_record.md5_hash,
                'sha256_hash': file_record.sha256_hash,
                'stored_path': file_record.stored_path,
                'metadata': json.loads(file_record.meta_data) if file_record.meta_data else None
            })
        
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error getting files: {e}")
        if session:
            session.close()
        return []

#
# C2 Server Management
#

def register_c2_server(name: str, server_type: str, host: str, port: int,
                     use_ssl: bool = True, auth_token: Optional[str] = None,
                     api_key: Optional[str] = None, username: Optional[str] = None,
                     password: Optional[str] = None,
                     configuration: Optional[Dict[str, Any]] = None) -> Optional[int]:
    """
    Register a C2 server.
    
    Args:
        name: Name of the C2 server
        server_type: Type of server (internal, covenant, mythic, etc.)
        host: Hostname or IP address
        port: Port number
        use_ssl: Whether to use SSL
        auth_token: Optional authentication token
        api_key: Optional API key
        username: Optional username
        password: Optional password
        configuration: Optional configuration dictionary
        
    Returns:
        C2 server ID if successful, None otherwise
    """
    try:
        session = get_session()
        if not session:
            return None
        
        # Check if server already exists
        existing_server = session.query(C2Server).filter(C2Server.name == name).first()
        if existing_server:
            # Update existing server
            existing_server.server_type = server_type
            existing_server.host = host
            existing_server.port = port
            existing_server.use_ssl = use_ssl
            existing_server.auth_token = auth_token
            existing_server.api_key = api_key
            existing_server.username = username
            existing_server.password = password
            
            if configuration:
                existing_server.configuration = json.dumps(configuration)
            
            session.commit()
            server_id = existing_server.id
            
            logger.info(f"Updated existing C2 server {name} (ID: {server_id})")
        else:
            # Create new server
            server = C2Server(
                name=name,
                server_type=server_type,
                host=host,
                port=port,
                use_ssl=use_ssl,
                auth_token=auth_token,
                api_key=api_key,
                username=username,
                password=password,
                configuration=json.dumps(configuration) if configuration else None
            )
            
            session.add(server)
            session.commit()
            server_id = server.id
            
            logger.info(f"Registered new C2 server {name} (ID: {server_id})")
        
        session.close()
        return server_id
    
    except Exception as e:
        logger.error(f"Error registering C2 server: {e}")
        if session:
            session.rollback()
            session.close()
        return None

def get_c2_servers(server_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get C2 servers.
    
    Args:
        server_type: Optional server type to filter by
        
    Returns:
        List of C2 servers
    """
    try:
        session = get_session()
        if not session:
            return []
        
        query = session.query(C2Server)
        
        if server_type:
            query = query.filter(C2Server.server_type == server_type)
        
        servers = query.all()
        
        result = []
        for server in servers:
            result.append({
                'id': server.id,
                'name': server.name,
                'server_type': server.server_type,
                'host': server.host,
                'port': server.port,
                'use_ssl': server.use_ssl,
                'status': server.status,
                'last_start_time': server.last_start_time,
                'last_stop_time': server.last_stop_time
            })
        
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error getting C2 servers: {e}")
        if session:
            session.close()
        return []

def update_c2_server_status(server_id: int, status: str, start: bool = False, stop: bool = False) -> bool:
    """
    Update C2 server status.
    
    Args:
        server_id: ID of the C2 server
        status: New status
        start: Set start time if True
        stop: Set stop time if True
        
    Returns:
        True if successful, False otherwise
    """
    try:
        session = get_session()
        if not session:
            return False
        
        server = session.query(C2Server).filter(C2Server.id == server_id).first()
        
        if not server:
            session.close()
            return False
        
        server.status = status
        
        if start:
            server.last_start_time = datetime.datetime.utcnow()
        
        if stop:
            server.last_stop_time = datetime.datetime.utcnow()
        
        session.commit()
        session.close()
        
        logger.info(f"Updated C2 server {server_id} status to '{status}'")
        return True
    
    except Exception as e:
        logger.error(f"Error updating C2 server status: {e}")
        if session:
            session.rollback()
            session.close()
        return False

#
# Credential Management
#

def store_credential(operation_id: int, credential_type: str, source: str,
                   username: Optional[str] = None, password: Optional[str] = None,
                   agent_id: Optional[str] = None, host: Optional[str] = None,
                   service: Optional[str] = None, 
                   metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
    """
    Store a credential.
    
    Args:
        operation_id: ID of the operation
        credential_type: Type of credential (password, hash, token, cookie, etc.)
        source: Source of the credential (browser, memory, keylogger, etc.)
        username: Optional username
        password: Optional password or hash
        agent_id: Optional agent ID
        host: Optional host
        service: Optional service
        metadata: Optional metadata dictionary
        
    Returns:
        Credential ID if successful, None otherwise
    """
    try:
        session = get_session()
        if not session:
            return None
        
        # Resolve agent database ID if agent_id is provided
        agent_db_id = None
        if agent_id:
            agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
            if agent:
                agent_db_id = agent.id
        
        # Create credential record
        credential = Credential(
            operation_id=operation_id,
            agent_id=agent_db_id,
            username=username,
            password=password,
            credential_type=credential_type,
            source=source,
            host=host,
            service=service,
            meta_data=json.dumps(metadata) if metadata else None
        )
        
        session.add(credential)
        session.commit()
        
        credential_id = credential.id
        session.close()
        
        logger.info(f"Stored {credential_type} credential (ID: {credential_id})")
        return credential_id
    
    except Exception as e:
        logger.error(f"Error storing credential: {e}")
        if session:
            session.rollback()
            session.close()
        return None

def get_credentials(operation_id: int, credential_type: Optional[str] = None,
                  source: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get credentials for an operation.
    
    Args:
        operation_id: ID of the operation
        credential_type: Optional credential type to filter by
        source: Optional source to filter by
        limit: Maximum number of credentials to return
        offset: Offset for pagination
        
    Returns:
        List of credentials
    """
    try:
        session = get_session()
        if not session:
            return []
        
        query = session.query(Credential).filter(Credential.operation_id == operation_id)
        
        if credential_type:
            query = query.filter(Credential.credential_type == credential_type)
        
        if source:
            query = query.filter(Credential.source == source)
        
        credentials = query.order_by(Credential.collect_time.desc()).limit(limit).offset(offset).all()
        
        result = []
        for credential in credentials:
            result.append({
                'id': credential.id,
                'operation_id': credential.operation_id,
                'agent_id': credential.agent_id,
                'username': credential.username,
                'password': credential.password,
                'credential_type': credential.credential_type,
                'source': credential.source,
                'host': credential.host,
                'service': credential.service,
                'collect_time': credential.collect_time,
                'metadata': json.loads(credential.meta_data) if credential.meta_data else None
            })
        
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error getting credentials: {e}")
        if session:
            session.close()
        return []

#
# Configuration Management
#

def store_configuration(config_name: str, config_section: str, config_data: Dict[str, Any]) -> bool:
    """
    Store a configuration.
    
    Args:
        config_name: Name of the configuration
        config_section: Section of the configuration
        config_data: Configuration data dictionary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        session = get_session()
        if not session:
            return False
        
        # Check if configuration already exists
        existing_config = session.query(Configuration).filter(
            Configuration.config_name == config_name
        ).first()
        
        if existing_config:
            # Update existing configuration
            existing_config.config_section = config_section
            existing_config.config_data = config_data
            existing_config.last_updated = datetime.datetime.utcnow()
        else:
            # Create new configuration
            config = Configuration(
                config_name=config_name,
                config_section=config_section,
                config_data=config_data
            )
            session.add(config)
        
        session.commit()
        session.close()
        
        logger.info(f"Stored configuration '{config_section}.{config_name}'")
        return True
    
    except Exception as e:
        logger.error(f"Error storing configuration: {e}")
        if session:
            session.rollback()
            session.close()
        return False

def get_configuration(config_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a configuration by name.
    
    Args:
        config_name: Name of the configuration
        
    Returns:
        Configuration data dictionary or None if not found
    """
    try:
        session = get_session()
        if not session:
            return None
        
        config = session.query(Configuration).filter(
            Configuration.config_name == config_name
        ).first()
        
        if not config:
            session.close()
            return None
        
        result = {
            'id': config.id,
            'config_name': config.config_name,
            'config_section': config.config_section,
            'config_data': config.config_data,
            'last_updated': config.last_updated
        }
        
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        if session:
            session.close()
        return None

def get_configurations_by_section(config_section: str) -> List[Dict[str, Any]]:
    """
    Get configurations by section.
    
    Args:
        config_section: Section of the configuration
        
    Returns:
        List of configuration data dictionaries
    """
    try:
        session = get_session()
        if not session:
            return []
        
        configs = session.query(Configuration).filter(
            Configuration.config_section == config_section
        ).all()
        
        result = []
        for config in configs:
            result.append({
                'id': config.id,
                'config_name': config.config_name,
                'config_section': config.config_section,
                'config_data': config.config_data,
                'last_updated': config.last_updated
            })
        
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error getting configurations: {e}")
        if session:
            session.close()
        return []