# Little Agent Chatbot - SQL Database Support 🚀

## New Feature Overview

**Little Agent Chatbot** now supports SQL database integration! Your chatbot can now retrieve data from local SQL databases, enabling powerful data-driven conversations and queries.

### ✅ Tested Database Support
- **MariaDB** - Fully tested and supported
- **Extensible** - Deploy any database with a Python interface

---

## How It Works

The chatbot uses an intelligent agent approach to interpret natural language queries and convert them into appropriate SQL statements. Here's a practical example:

### Sample Database Structure

```sql
MariaDB [MYSTORE]> desc FRUITS;
+----------+-------------+------+-----+---------+-------+
| Field    | Type        | Null | Key | Default | Extra |
+----------+-------------+------+-----+---------+-------+
| ITEM     | varchar(50) | YES  |     | NULL    |       |
| QUANTITY | int(11)     | YES  |     | NULL    |       |
+----------+-------------+------+-----+---------+-------+
2 rows in set (0.001 sec)

MariaDB [MYSTORE]> select * from FRUITS;
+---------+----------+
| ITEM    | QUANTITY |
+---------+----------+
| APPLES  |        2 |
| ORANGE  |        3 |
| APRICOT |        5 |
| GRAPES  |        4 |
| BANANA  |        1 |
+---------+----------+
5 rows in set (0.000 sec)
```

### Natural Language Query Example

**User Prompt:** *"Do we have orange in our warehouse?"*

---

## LLM Performance Comparison

### 🦙 LLM: llama3.2:3b

```
Entering new AgentExecutor chain...
Invoking: `get_SQL_response` with `{'SQL_statement': 'SELECT ITEM, QUANTITY FROM FRUITS'}`

--- Running Query ---
Connecting to MariaDB...
Connection successful.
Connection closed.

APPLES, 2
ORANGE, 3
APRICOT, 5
GRAPES, 4
BANANA, 1

Response: Based on the response from our warehouse management system, we do have oranges in stock. The quantity of oranges available is 3 units.
```

### 🤖 LLM: qwen3:1.7b

```
Entering new AgentExecutor chain...
Invoking: `get_SQL_response` with `{'SQL_statement': "SELECT ITEM, QUANTITY FROM FRUITS WHERE ITEM = 'orange';"}`

--- Running Query ---
Connecting to MariaDB...
Connection successful.
Connection closed.

ORANGE, 3

Response: Yes, we have orange in the warehouse. The quantity available is 3 units.
```

> **Note:** Notice how different LLMs approach the same query - some use broader SELECT statements while others optimize with WHERE clauses.

---

## Installation Guide

### Prerequisites
Ensure you have the basic **Little Agent Chatbot** installed first.

### Step 1: Install MariaDB

```bash
# Install MariaDB server and client
sudo apt install mariadb-server mariadb-client

# Secure the installation
sudo mariadb-secure-installation
```

### Step 2: Create Sample Database

```bash
# Connect to MariaDB
mariadb -u root -p -h localhost
```

Then execute the following SQL commands:

```sql
-- Create database and table
CREATE DATABASE MYSTORE;
USE MYSTORE;

CREATE TABLE FRUITS (
    ITEM VARCHAR(50),
    QUANTITY INT
);

-- Insert sample data
INSERT INTO FRUITS VALUES 
    ("APPLES", 2),
    ("ORANGE", 3),
    ("APRICOT", 5),
    ("GRAPES", 4),
    ("BANANA", 1);

-- Exit MariaDB
quit;
```

### Step 3: Install Python Dependencies & Configure

```bash
# Install MariaDB Python connector
pip install mariadb

# Add database credentials to environment file
echo 'DB_USER=your_maria_db_user' >> .env
echo 'DB_PASSWORD=your_maria_db_password' >> .env
```

---

## 🎯 Key Benefits

- **Natural Language Processing** - Ask questions in plain English
- **Intelligent Query Generation** - LLM converts natural language to SQL
- **Database Agnostic** - Easily adaptable to other database systems
- **Real-time Data Access** - Get live data from your databases
- **Contextual Responses** - Receive human-friendly answers to data queries

---

## 🔧 Customization

Want to use a different database? Simply:

1. Install the appropriate Python database connector
2. Update the connection configuration
3. Modify the `get_SQL_response` function accordingly

---

*Happy coding! 🚀*



