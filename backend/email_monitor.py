"""
Background Email Monitor
Automatically checks for new transaction emails every 45 seconds
"""

import time
import threading
from datetime import datetime
from process_transactions import process_all_transactions
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration
CHECK_INTERVAL = 45  # 45 seconds
USER_ID = os.getenv("DEFAULT_USER_ID", "demo_user")

# Flag to control the monitoring
monitoring_active = True


def monitor_emails():
    """
    Background task that checks for new emails periodically
    """
    global monitoring_active
    
    print("\n" + "="*60)
    print("🔄 EMAIL MONITORING STARTED")
    print("="*60)
    print(f"⏱️  Checking every {CHECK_INTERVAL} seconds")
    print(f"👤 User: {USER_ID}")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    check_count = 0
    
    while monitoring_active:
        try:
            check_count += 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"\n{'='*60}")
            print(f"🔍 Check #{check_count} at {current_time}")
            print(f"{'='*60}\n")
            
            # Process transactions
            result = process_all_transactions(USER_ID)
            
            if result['success']:
                if result['total_new'] > 0:
                    print(f"\n✅ Added {result['total_new']} new transaction(s)!")
                else:
                    print(f"\n✓ No new transactions found")
            else:
                print(f"\n⚠️ Check failed: {result.get('message', 'Unknown error')}")
            
            # Wait for next check
            if monitoring_active:
                from datetime import timedelta
                next_check = datetime.now() + timedelta(seconds=CHECK_INTERVAL)
                print(f"\n⏳ Next check at: {next_check.strftime('%H:%M:%S')}")
                print(f"💤 Sleeping for {CHECK_INTERVAL} seconds...")
                
                # Sleep in small intervals to allow for graceful shutdown
                for _ in range(CHECK_INTERVAL):
                    if not monitoring_active:
                        break
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n⚠️ Monitoring stopped by user")
            monitoring_active = False
            break
        except Exception as e:
            print(f"\n❌ Error during monitoring: {e}")
            print("⏳ Will retry in next cycle...")
            time.sleep(60)  # Wait 1 minute before retry on error


def start_monitoring_thread():
    """
    Start email monitoring in a background thread
    """
    monitor_thread = threading.Thread(target=monitor_emails, daemon=True)
    monitor_thread.start()
    return monitor_thread


def stop_monitoring():
    """
    Stop the email monitoring
    """
    global monitoring_active
    monitoring_active = False
    print("\n🛑 Stopping email monitoring...")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("📧 AUTOMATIC EMAIL MONITOR")
    print("="*60)
    print("\nThis script will automatically check for new transaction emails")
    print(f"and add them to your account every {CHECK_INTERVAL} seconds.")
    print("\nPress Ctrl+C to stop monitoring.\n")
    print("="*60)
    
    try:
        monitor_emails()
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped successfully")
        print("="*60 + "\n")
