import requests
import json

BLOCK_DIFFERENCE_THRESHOLD=10

print("""
  _____  _____   _____ ____  _            _     _____                  
 |  __ \|  __ \ / ____|  _ \| |          | |   / ____|                 
 | |__) | |__) | |    | |_) | | ___   ___| | _| (___  _   _ _ __   ___ 
 |  _  /|  ___/| |    |  _ <| |/ _ \ / __| |/ /\___ \| | | | '_ \ / __|
 | | \ \| |    | |____| |_) | | (_) | (__|   < ____) | |_| | | | | (__ 
 |_|  \_\_|     \_____|____/|_|\___/ \___|_|\_\_____/ \__, |_| |_|\___|
                                                       __/ |           
                                                      |___/  by: arddluma
""")

def check_block_sync(rpc_endpoints, endpoint_urls, label):
    block_numbers = []
    for endpoint in rpc_endpoints:
        try:
            response = requests.post(endpoint, json={'jsonrpc': '2.0', 'id': 1, 'method': 'eth_blockNumber'})
            response.raise_for_status()
            result = response.json()['result']
            block_numbers.append(int(result, 16))
            issue = False
        except Exception as e:
            print(f"{endpoint} Something went wrong with one of the RPCs\n {e}")
            issue = True
            message = ""

    if issue == False:
        if len(set(block_numbers)) == 1:
            print(f"All RPC endpoints for {label} are in sync at block: {block_numbers[0]}\n\n")
            message = ""
        else:
            message = f"Block number differences detected for {label}:\n"
            print(f"Block number differences detected for {label}:\n")
            for i, block_number in enumerate(block_numbers):
                if max(block_numbers) - min(block_numbers) > BLOCK_DIFFERENCE_THRESHOLD:
                    print(f"RPC endpoint {endpoint_urls[i]} at block: {block_number}\n")
                    message += f"RPC endpoint {endpoint_urls[i]} at block: *{block_number}*\n"
            if max(block_numbers) - min(block_numbers) > BLOCK_DIFFERENCE_THRESHOLD:
                difference = max(block_numbers) - min(block_numbers)
                message += f"\nDifference ({difference}) is greater than threshold {BLOCK_DIFFERENCE_THRESHOLD} blocks!\n"
                print(f"\n{label} Difference ({difference}) is greater than threshold {BLOCK_DIFFERENCE_THRESHOLD} blocks!\nSending Slack notification...")
            else:
                message = ""
                difference = max(block_numbers) - min(block_numbers)
                print(f"{label} Difference ({difference}) is less than or equal to {BLOCK_DIFFERENCE_THRESHOLD} blocks!\n")
                for i, block_number in enumerate(block_numbers):
                    if max(block_numbers) - min(block_numbers) < BLOCK_DIFFERENCE_THRESHOLD:
                        print(f"RPC endpoint {endpoint_urls[i]} at block {block_number}\n")
        return message


with open('rpc_endpoints.txt', 'r') as f:
    endpoints_by_label = {}
    current_label = ""
    for line in f:
        line = line.strip()
        if line:
            if ":" in line:
                current_label, endpoints = line.split(":", 1)
                endpoints_by_label[current_label] = [endpoint.strip() for endpoint in endpoints.split(";")]
            else:
                endpoints_by_label[current_label].extend([endpoint.strip() for endpoint in line.split(";")])

message = ""
for label, rpc_endpoints in endpoints_by_label.items():
    endpoint_urls = [endpoint for endpoint in rpc_endpoints]
    message += check_block_sync(rpc_endpoints, endpoint_urls, label)

slack_webhook_url = "https://hooks.slack.com/services/xxxxxx/xxxxx/xxxxx" #### https://api.slack.com/messaging/webhooks
slack_message = {
    "text": message
}
try:
    send_slack_message = requests.post(slack_webhook_url, json.dumps(slack_message))
    send_slack_message.raise_for_status()
except Exception as e:
    print(f"Failed to send Slack message: {e}")
else:
    print("Slack message sent successfully!")
