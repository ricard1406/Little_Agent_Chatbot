## 🔮 WORKING IN PROGRESS

-  SQL database agent support
-  Chatbot can retrive data from local SQL database
-  testing MariaDB support

```
example:
this is our table:

MariaDB [MYSTORE]> desc FRUITS;
+----------+-------------+------+-----+---------+-------+|
 Field    | Type        | Null | Key | Default | Extra |
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

This is our Prompt : do we have orange in our warehouse ?

(LLM llama3.2:3b)..... Entering new AgentExecutor chain...
Invoking: `get_SQL_response` with `{'SQL_statement': 'SELECT ITEM, QUANTITY FROM FRUITS'} 
--- Running Query ---
Connecting to MariaDB...
Connection successful.
Connection closed.
APPLES, 2
ORANGE, 3
APRICOT, 5
GRAPES, 4
BANANA, 1
Based on the response from our warehouse management system, we do have oranges in stock. The quantity of oranges available is 3 units.

(LLM qwen3:1.7b) ....... Entering new AgentExecutor chain...
Invoking: `get_SQL_response` with `{'SQL_statement': "SELECT ITEM, QUANTITY FROM FRUITS WHERE ITEM = 'orange';"}`
--- Running Query ---
Connecting to MariaDB...
Connection successful.
Connection closed.
ORANGE, 3<think>
Okay, the user asked if we have orange in the warehouse. I called the get_SQL_response function with a query to check the FRUITS table for orange. The response came back as ORANGE, 3. So, that means the warehouse has orange items with a quantity of 3. I need to relay this information clearly to the user. Let me make sure to state the item and the quantity accurately. Also, check if there's any need for additional information, but since the user just asked if there's orange, confirming the presence and quantity should be sufficient.
</think>

We currently have ORANGE with a quantity of 3 in the warehouse.



