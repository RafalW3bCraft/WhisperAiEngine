#!/usr/bin/env python3

import sys
import os
import json

# Ensure we're in the project directory
project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_dir)

from src.exploitation.post.privilege_escalation import scan_for_privesc_vectors, exploit_suid_binary

def main():
    """Test privilege escalation scanner"""
    print("Testing privilege escalation scanner...")
    
    # Perform a privilege escalation scan
    print("\nScanning for privilege escalation vectors...")
    results = scan_for_privesc_vectors()
    
    # Print results in human-readable format
    print("\nPrivilege Escalation Vectors:")
    
    if 'suid_files' in results:
        exploitable_suid = [f for f in results['suid_files'] if f['is_exploitable']]
        
        if exploitable_suid:
            print("\nExploitable SUID Binaries:")
            for suid in exploitable_suid:
                print(f"  {suid['file']} (owned by {suid['owner']})")
                print(f"    {suid['exploit_info']}")
                
                # Generate exploit for the first exploitable binary
                if len(exploitable_suid) > 0:
                    suid_path = exploitable_suid[0]['file']
                    print(f"\nGenerating exploit for {suid_path}:")
                    exploit_info = exploit_suid_binary(suid_path)
                    
                    if exploit_info['exploitable']:
                        print(f"Instructions: {exploit_info['instructions']}")
                        print("\nExploit Commands:")
                        for cmd in exploit_info['commands']:
                            print(f"  {cmd}")
                    else:
                        print(f"Not exploitable: {exploit_info['instructions']}")
    
    # Save full results to JSON file
    with open('privesc_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nFull results saved to privesc_results.json")

if __name__ == "__main__":
    main()