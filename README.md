# VKinder

VKontakte bot for finding a partner by preference

## Table of contents
  * [Overview](#Overview)
  * [Project Structure](#Project-Structure)
  * [Database Structure](#Database-Structure)
  * [Setup and Installation](#Setup-and-Installation)
    * [PostgreSQL](#PostgreSQL)
    * [Python](#Python)
    * [VKontakteBot](#VKontakteBot)
  * [Running the Program](#Running-the-Program)
  * [Demonstration of the program](#Demonstration-of-the-program)

## Overview
VKontakte bot that searches for people to date

### Key Features:
1. The bot searches for a reliable partner based on several options: city, age range, gender
2. Search options can be changed at any time via the settings menu 
3. The found pair can be saved to the list of favorites or blacklist
4. Through chat with the bot you can view favorites and blacklists, get photos of person and remove them from the list

## Project Structure
```
VKinder /
├── images/ # photos for README
├── src/
│   ├── settings.py - setting config creator
│   ├── bot/
│   │   ├── bot.py - logic of the bot's response to user actions
│   │   ├── base.py - base class of bot
│   │   ├── constants.py - constants for bot
│   │   ├── formatters.py - functions for formatting variables into a string
│   │   ├── keyboard.py - templates for buttons in bot chat
│   │   ├── message_processing.py - getting data from messages from a user
│   │   ├── message_texts.py - bot message texts
│   │   ├── partner.py - class for finding and interacting with partners
│   │   ├── setting.py - class for search settings
│   │   ├── show_messages.py - class for displaying various menus
│   │   ├── types.py - bot type structures
│   │   ├── utils.py - bot misc functions
│   ├── db/
│   │   ├── database.py - database sctructure logic
│   │   ├── db_manager.py - database interaction manager
│   └── vk_api/ 
│       ├── api.py - methods of VK API interaction for the bot
│       ├── keyboard.py - abstraction of the JSON object Keyboard method of messages.send VK API
│       ├── logger.py - logger initializer for VK API requests 
│       ├── service.py - VK API request handler
│       └── types.py - api type structures
├── .env.example - example of .env file
├── requirements.txt - project requirements
└── README.md
```

## Database Structure
![](images/vkinder_db_diagram.png)
### Tables List:
* *Users* - vk id list for each user
* *Dialog_state* - state of dialogue with the user
* *User_settings* - search settings for user
* *Temp_settings* - user temporary search settings data before installation
* *Cities* - list of city names
* *Regions* - list of region names
* *Favorites* - list of favorite partners
* *Blacklist* - list of blacklisted partners
* *Partner_info* - information about the partner
* *Photos* - partner's photo data

## Setup and Installation

### PostgreSQL

This project uses PostgreSQL for data storage.

1. Installing and setting-up PostgreSQL server following this [guide](https://medium.com/@dan.chiniara/installing-postgresql-for-windows-7ec8145698e3)
2. Log into the psql client via the terminal using the admin account
   
   ```$ psql -U <admin_username>```

3. Create new user (optional)

   ```postgres=# CREATE USER username WITH PASSWORD 'username_password';```

4. Create database
   
   ```postgres=# CREATE DATABASE database_name;```

### Python

This project depends on Python version 3.12 or higher.

1. Cloning repository
   
   ```$ git clone https://github.com/samboed/VKinder.git ``` 

2. Go to the cloned directory
   
   ```$ cd VKinder ``` 

3. Create virtual environment
   
   ```$ python -m venv .venv ``` 

4. Activate virtual environment:

* Windows (CMD): ```> .venv\Scripts\activate.bat```
* Windows (PowerShell): ```> .venv\Scripts\Activate.ps1```
* Linux: ```$ source .venv\Scripts\activate```

5. Install requirements
   
   ```$ pip install -r requirements.txt```

### VKontakteBot

To use the program, you need to create VK group bot and get group, user API token

1. Go to the https://vk.com/groups and click **Создать сообщество**
   
   ![](images/vk_bot_creation/group_creation.png)
   
2. Select a community goal
3. Enter a name for your community and select a topic. Optionally, add other parameters
4. Go to the community you created
5. The group ID (**GROUP_ID**) can be taken in main group page from address bar

   ![](images/vk_bot_creation/group_id.png)
   
6. From the menu on the right select **Управление**

   ![](images/vk_bot_creation/select_group_management.png)

7. From the open menu, select **Дополнительно → Работа с API**

   ![](images/vk_bot_creation/group_token_creation.png)

8. Click **Создать ключ**

   ![](images/vk_bot_creation/click_create_key.png)

10. Select the right of access to community messages and confirm your choice
   
   ![](images/vk_bot_creation/group_setup_rights.png)

11. The group API token (**TOKEN_GROUP**) will appear in **Ключи доступа** tab

12. Switch to the Long Poll API tab. Turn on Long Poll API and select API version **5.199**

    ![](images/vk_bot_creation/vk_api_configuration.png)

13. To get a user API token (**TOKEN_USER**), go to https://vkhost.github.io/ and follow the instructions by selecting the app vk.com

## Running the Program

1. Copy **.env.example** to **.env** file

   ```$ copy .env.example .env```

2. Fill **.env** file:

   ```
   # VK API
   TOKEN_GROUP:your_vk_api_group_token
   GROUP_ID:your_group_id
   TOKEN_USER:your_vk_api_user_token

   # Database
   # driver://username:password@hostname:5432/database_name
   DSN:dsn_database
   ```

3. Run main.py from pre-configured virtual environment:

   ```$ python main.py```

## Demonstration of the program

[Watch on YouTube]()


