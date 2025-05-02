#!/usr/bin/env python3
# Test script for G3r4ki's self-improvement capabilities

import os
import sys
import time
import logging
import datetime
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('g3r4ki.test')

# Ensure we're in the project directory
project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_dir)

from src.config import setup_config
from src.enhancement.self_improvement import SelfImprovementManager

def test_usage_tracking():
    """Test command usage tracking"""
    config = setup_config()
    manager = SelfImprovementManager(config)
    
    # Record some simulated command usage
    logger.info("Recording simulated command usage...")
    commands = [
        ("llm query", True, 1.5),
        ("scan 192.168.1.1", True, 3.2),
        ("exploit webshell", True, 0.8),
        ("recon example.com", False, 2.1),
        ("vuln scan", True, 5.3),
    ]
    
    for cmd, success, duration in commands:
        manager.record_command_usage(cmd, success, duration)
        logger.info(f"Recorded: {cmd} (success={success}, duration={duration}s)")
    
    logger.info("Command usage tracking test completed")
    return True

def test_performance_monitoring():
    """Test performance monitoring"""
    config = setup_config()
    manager = SelfImprovementManager(config)
    
    # Record some simulated performance metrics
    logger.info("Recording simulated performance metrics...")
    for i in range(5):
        # Simulate response time (seconds)
        response_time = 0.8 + (i * 0.2)
        
        # Simulate memory usage (MB)
        memory_usage = 200 + (i * 20)
        
        manager.record_performance_metrics(response_time, memory_usage)
        logger.info(f"Recorded metrics: response_time={response_time}s, memory_usage={memory_usage}MB")
        
    logger.info("Performance monitoring test completed")
    return True

def test_error_tracking():
    """Test error tracking"""
    config = setup_config()
    manager = SelfImprovementManager(config)
    
    # Record some simulated errors
    logger.info("Recording simulated errors...")
    errors = [
        ("llm.query", "Failed to connect to OpenAI API", {"provider": "openai"}),
        ("network.scan", "Timeout connecting to target", {"target": "192.168.1.1"}),
        ("exploit.webshell", "Invalid target parameter", {"target": "example.com"}),
    ]
    
    for component, message, context in errors:
        manager.record_error(component, message, context)
        logger.info(f"Recorded error: {component} - {message}")
    
    logger.info("Error tracking test completed")
    return True

def test_learning():
    """Test learning from successful operations"""
    config = setup_config()
    manager = SelfImprovementManager(config)
    
    # Record some simulated successful operations
    logger.info("Recording simulated successful operations...")
    
    # Scan operation
    scan_details = {
        "target_type": "web_application",
        "target": "example.com",
        "options": {
            "port_scan": True,
            "service_detection": True,
            "vulnerability_check": True
        },
        "duration": 45.2
    }
    
    scan_outcome = {
        "success": True,
        "findings": [
            {"type": "open_port", "details": "Port 80 (HTTP) is open"},
            {"type": "open_port", "details": "Port 443 (HTTPS) is open"},
            {"type": "service", "details": "Apache 2.4.41 on port 80"},
            {"type": "vulnerability", "details": "CVE-2021-12345 in Apache"}
        ]
    }
    
    manager.learn_from_successful_operation("scan", scan_details, scan_outcome)
    logger.info("Recorded successful scan operation")
    
    # Exploit operation
    exploit_details = {
        "vulnerability_type": "sql_injection",
        "target_os": "linux",
        "target": "vulnerable-app.example.com",
        "parameters": {
            "injection_point": "id=",
            "payload": "1' OR '1'='1"
        }
    }
    
    exploit_outcome = {
        "success": True,
        "access_gained": True,
        "access_level": "database_user",
        "success_factors": [
            "No input validation",
            "Error messages exposed",
            "Database privileges not restricted"
        ]
    }
    
    manager.learn_from_successful_operation("exploit", exploit_details, exploit_outcome)
    logger.info("Recorded successful exploit operation")
    
    logger.info("Learning from operations test completed")
    return True

def test_self_improvement():
    """Test self-improvement routine"""
    config = setup_config()
    manager = SelfImprovementManager(config)
    
    # Run self-improvement with force=True to ensure it runs
    logger.info("Running self-improvement routine...")
    result = manager.run_self_improvement(force=True)
    
    if result['status'] == 'success':
        logger.info("Self-improvement completed successfully")
        
        # Show results
        for key, value in result['results'].items():
            if isinstance(value, dict) and 'status' in value:
                status = value['status']
                details = ""
                
                if 'optimizations' in value and value['optimizations']:
                    details = f" - {len(value['optimizations'])} optimizations"
                elif 'improvements' in value and value['improvements']:
                    details = f" - {len(value['improvements'])} improvements"
                
                logger.info(f"  {key}: {status}{details}")
    else:
        logger.error(f"Self-improvement failed: {result.get('message', 'Unknown error')}")
    
    return result['status'] == 'success'

def test_enhancement_stats():
    """Test getting enhancement statistics"""
    config = setup_config()
    manager = SelfImprovementManager(config)
    
    logger.info("Getting enhancement statistics...")
    stats = manager.get_enhancement_stats()
    
    logger.info(f"Last improvement: {datetime.datetime.fromtimestamp(stats['last_improvement'])}")
    logger.info(f"Next improvement: {datetime.datetime.fromtimestamp(stats['next_improvement'])}")
    
    for stat, value in stats['cumulative_stats'].items():
        logger.info(f"  {stat}: {value}")
    
    if stats['recent_activity']:
        logger.info("Recent activity:")
        for activity in stats['recent_activity']:
            timestamp = datetime.datetime.fromtimestamp(activity['timestamp'])
            logger.info(f"  {timestamp}: {activity['summary']}")
    
    return True

def test_learning_insights():
    """Test getting learning insights"""
    config = setup_config()
    manager = SelfImprovementManager(config)
    
    logger.info("Getting learning insights...")
    insights = manager.get_learning_insights()
    
    if insights['frequent_patterns']:
        logger.info("Frequent patterns:")
        for op_type, patterns in insights['frequent_patterns'].items():
            logger.info(f"  {op_type}:")
            for pattern in patterns:
                logger.info(f"    {pattern['pattern']} (count: {pattern['count']})")
    
    if insights['workflow_recommendations']:
        logger.info("Workflow recommendations:")
        for recommendation in insights['workflow_recommendations']:
            logger.info(f"  {recommendation['type']}: {recommendation['recommendation']}")
            logger.info(f"    Effectiveness: {recommendation['effectiveness']}")
    
    return True

def main():
    """Run tests for self-improvement capabilities"""
    logger.info("Starting G3r4ki self-improvement tests")
    
    tests = [
        ("Usage tracking", test_usage_tracking),
        ("Performance monitoring", test_performance_monitoring),
        ("Error tracking", test_error_tracking),
        ("Learning from operations", test_learning),
        ("Self-improvement routine", test_self_improvement),
        ("Enhancement statistics", test_enhancement_stats),
        ("Learning insights", test_learning_insights),
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"\n--- Running test: {name} ---")
        try:
            success = test_func()
            status = "PASSED" if success else "FAILED"
            results.append((name, status))
            logger.info(f"--- Test {name}: {status} ---\n")
        except Exception as e:
            logger.error(f"Error in test {name}: {str(e)}")
            results.append((name, "ERROR"))
            logger.info(f"--- Test {name}: ERROR ---\n")
    
    # Show summary
    logger.info("\n=== Test Summary ===")
    for name, status in results:
        logger.info(f"{name}: {status}")
    
    # Count results
    passed = sum(1 for _, status in results if status == "PASSED")
    failed = sum(1 for _, status in results if status == "FAILED")
    errors = sum(1 for _, status in results if status == "ERROR")
    
    logger.info(f"\nTotal: {len(results)}, Passed: {passed}, Failed: {failed}, Errors: {errors}")
    
    return passed == len(results)

if __name__ == "__main__":
    main()