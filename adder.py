#!/usr/bin/env python3
# (c) @AbirHasan2005
# Telegram Group: http://t.me/linux_repo
# Please give me credits if you use any codes from here.

import sys
import csv
import traceback
import time
import random
from telethon.sync import TelegramClient
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser

# ANSI escape sequences for colored output
print("\033[1;92m")
print("░█▀█░█▀▄░█▀▄░█▀▀░█▀▄")
print("░█▀█░█░█░█░█░█▀▀░█▀▄")
print("░▀░▀░▀▀░░▀▀░░▀▀▀░▀░▀")
print("")
print("      by \033[1;95m@AbirHasan2005")
print("\033[1;92m")

# Replace these with your actual credentials
api_id = 28913428  # Your 7 Digit Telegram API ID
api_hash = 'd0800fa85a7225743a91e2d89364baf1'  # Your 32 Character API Hash
phone = '+16135026024'  # Your Mobile Number With Country Code

# Initialize the Telegram client
client = TelegramClient(phone, api_id, api_hash)

def authenticate_client():
    try:
        client.start()
    except Exception as e:
        print(f"Failed to start client: {e}")
        sys.exit(1)

def load_users(csv_file):
    users = []
    try:
        with open(csv_file, encoding='UTF-8') as f:
            rows = csv.reader(f, delimiter=",", lineterminator="\n")
            next(rows, None)  # Skip header
            for row in rows:
                if len(row) < 4:
                    print(f"Skipping incomplete row: {row}")
                    continue
                user = {
                    'username': row[0],
                    'id': int(row[1]),
                    'access_hash': int(row[2]),
                    'name': row[3],
                }
                users.append(user)
    except FileNotFoundError:
        print(f"Error: The specified file '{csv_file}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading '{csv_file}': {e}")
        sys.exit(1)
    return users

def get_target_group():
    chats = []
    last_date = None
    chunk_size = 200  # Reduced chunk size to prevent overload
    groups = []

    try:
        result = client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))
        chats.extend(result.chats)

        for chat in chats:
            if hasattr(chat, 'megagroup') and chat.megagroup:
                groups.append(chat)

        if not groups:
            print("No groups found. Exiting.")
            sys.exit(1)

        print('Choose a group to add members: ')
        for i, group in enumerate(groups):
            print(f"{i} - {group.title}")

        while True:
            try:
                g_index = int(input("Enter a Number: "))
                if 0 <= g_index < len(groups):
                    break
                else:
                    print("Invalid number. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

        target_group = groups[g_index]
        target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)
        return target_group_entity
    except Exception as e:
        print(f"Failed to retrieve groups: {e}")
        sys.exit(1)

def add_users_to_group(target_group, users, mode):
    SLEEP_TIME_1 = 100
    SLEEP_TIME_2 = 100
    n = 0

    for user in users:
        n += 1
        if n % 80 == 0:
            print(f"Reached {n} users. Sleeping for {SLEEP_TIME_1} seconds to avoid rate limits.")
            time.sleep(SLEEP_TIME_1)
        try:
            print(f"Adding {user['name']} (ID: {user['id']})")
            if mode == 1:
                if user['username']:
                    user_to_add = client.get_input_entity(user['username'])
                else:
                    print(f"Username is empty for user {user['name']}, skipping...")
                    continue
            elif mode == 2:
                user_to_add = InputPeerUser(user['id'], user['access_hash'])
            else:
                print("Invalid mode selected. Exiting.")
                sys.exit(1)
            
            client(InviteToChannelRequest(target_group, [user_to_add]))
            print("Waiting for 60-180 Seconds...")
            time.sleep(random.randint(60, 180))  # Random sleep to mimic human behavior
        except PeerFloodError:
            print("Getting Flood Error from Telegram. Script is stopping now. Please try again after some time.")
            print(f"Waiting {SLEEP_TIME_2} seconds before exiting.")
            time.sleep(SLEEP_TIME_2)
            sys.exit(1)
        except UserPrivacyRestrictedError:
            print(f"The user's privacy settings do not allow you to do this. Skipping {user['name']}...")
            time.sleep(random.randint(5, 15))  # Short sleep before continuing
        except Exception as e:
            print(f"Unexpected Error for user {user['name']}: {e}")
            traceback.print_exc()
            time.sleep(random.randint(5, 15))
            continue

def main():
    authenticate_client()
    users = load_users("members.csv")
    target_group = get_target_group()

    while True:
        try:
            mode = int(input("Enter 1 to add by username or 2 to add by ID: "))
            if mode in [1, 2]:
                break
            else:
                print("Invalid selection. Please enter 1 or 2.")
        except ValueError:
            print("Please enter a valid number.")

    add_users_to_group(target_group, users, mode)
    print("Script has finished executing.")

if __name__ == "__main__":
    main()
