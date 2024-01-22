###瑞士制賽程
import random
import mysql.connector
from prettytable import PrettyTable

conn = mysql.connector.connect(
    host='YourHost',
    user='YourUsername',
    password='YourPassword',
    database='YourDatabase')

cursor = conn.cursor()


def __init__():
    try:
        # 建立連線和游標
        with conn.cursor() as cursor:
            # 刪除表格
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            drop_tables_queries = [f"DROP TABLE IF EXISTS {table[0]}" for table in tables]
            for query in drop_tables_queries:
                cursor.execute(query)

            # 刪除觸發器
            cursor.execute("SHOW TRIGGERS")
            triggers = cursor.fetchall()
            drop_trigger_queries = [f"DROP TRIGGER IF EXISTS {trigger[0]}" for trigger in triggers]
            for query in drop_trigger_queries:
                cursor.execute(query)

        # 提交更改
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")


# Setting
class WOL:
    W = 3
    L = 0
    T = 1


# 創建一參賽表#O
def Entrylist():
    create_table_query = """
    CREATE TABLE `Now_Players` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `Name` VARCHAR(255) NOT NULL,
    `Player_Rank` INT NOT NULL,
    `Player_ID` VARCHAR(255) NOT NULL,
    `Point` INT default 0,
    `OPW_percent` FLOAT default 0,
    `OpOPW_percent` FLOAT default 0,
    `Game` INT default 0 ,
    `Game_Win` INT default 0,
    `Win_percent` float default 0
    );
    """
    trigger1 = """
    CREATE TRIGGER update_win_percent
    BEFORE INSERT ON `Now_Players`
    FOR EACH ROW
    SET NEW.Win_percent = IFNULL(NEW.Game_Win / NULLIF(NEW.Game, 0), 0);
    """
    trigger2 = """
    CREATE TRIGGER dynamic_update_win_percent
    BEFORE UPDATE ON `Now_Players`
    FOR EACH ROW
    SET NEW.Win_percent = IFNULL(NEW.Game_Win / NULLIF(NEW.Game, 0), 0);
    """

    cursor.execute(create_table_query)
    cursor.execute(trigger1)
    cursor.execute(trigger2)
    conn.commit()

    m = int(input("參賽人數:"))

    for i in range(0, m):
        name = str(input("第{}位參賽者名稱:".format(i + 1)))
        player_id = str(input("第{}位參賽者ID:".format(i + 1)))
        create_players = """
            INSERT INTO `Now_Players` (`Name`, `Player_Rank`, `Player_ID`, `Point`)
        VALUES (%s, 0, %s, 0 );
        """

        create_player_table = f"""
            CREATE TABLE IF NOT EXISTS id_{player_id} (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `Point` INT DEFAULT 0,
                `OPW_percent` FLOAT DEFAULT 0,
                `Game` INT DEFAULT 0,
                `Game_Win` INT DEFAULT 0,
                `Win_percent` FLOAT DEFAULT 0,
                FOREIGN KEY (`id`) REFERENCES Now_Players(`id`)
            );
        """
        trigger3 = f"""
            CREATE TRIGGER `update_op{i + 1}`
                AFTER UPDATE ON `Now_Players`
                FOR EACH ROW
                UPDATE `id_{player_id}`
                SET `Point` = NEW.`Point`,
            	`OPW_percent` = NEW.`OPW_percent`,
                `Game` = NEW.`Game`,
                `Game_Win` = NEW.`Game_Win`,
                `Win_percent` = NEW.`Win_percent`
                WHERE id = NEW.id;"""
        cursor.execute(create_players, (name, player_id,))
        cursor.execute(create_player_table, )
        cursor.execute(trigger3)
        conn.commit()


## 輸入參賽者的資訊


# OPW_percent處理
def Renew_OPW():
    id_list_query = """
        SELECT
            `id`
        FROM
            `Now_Players`;
    """
    cursor.execute(id_list_query)
    list_id = cursor.fetchall()

    for i in list_id:
        select_query = f"""
                SELECT
                    AVG(COALESCE(`Win_percent`, 0)) AS avg_win_percent
                FROM
                    `id_{i[0]}`;
            """

        cursor.execute(select_query)
        a = cursor.fetchone()  # 使用 fetchone() 取得第一欄的值

        update_rank_query = f"""
            UPDATE `Now_Players`
            SET `OPW_percent` = {a[0] if a[0] is not None else 0}
            WHERE `id` = {i[0]};
        """
        cursor.execute(update_rank_query)

    conn.commit()


def Renew_OPopW():
    id_list_query = """
        SELECT
            `id`
        FROM
            `Now_Players`;
    """
    cursor.execute(id_list_query)
    list_id = cursor.fetchall()

    for i in list_id:
        select_query = f"""
                SELECT
                    AVG(COALESCE(`OPW_percent`, 0)) AS avg_OPW_percent
                FROM
                    `id_{i[0]}`;
            """

        cursor.execute(select_query)
        a = cursor.fetchone()  # 使用 fetchone() 取得第一欄的值

        update_rank_query = f"""
            UPDATE `Now_Players`
            SET `OpOPW_percent` = {a[0] if a[0] is not None else 0}
            WHERE `id` = {i[0]};
        """
        cursor.execute(update_rank_query)

    conn.commit()


# 更新當前排名表#O
def Renew():
    select_query = """
        SELECT
            `id`,
            ROW_NUMBER() OVER (ORDER BY `Point` DESC, `OPW_percent` DESC, `OpOPW_percent` DESC) AS `Player_Rank`
        FROM
            `Now_Players`
        ORDER BY
            `Point` DESC, `OPW_percent` DESC, `OpOPW_percent` DESC;
    """
    cursor.execute(select_query)
    result = cursor.fetchall()

    # 更新 `Now_Players` 表格中的 `Player_Rank`
    for row in result:
        player_id, player_rank = row[0], row[1]
        update_rank_query = """
            UPDATE `Now_Players`
            SET `Player_Rank` = %s
            WHERE `id` = %s;
        """
        cursor.execute(update_rank_query, (player_rank, player_id))

    conn.commit()


# #輪次設定及是否進入淘汰賽人數
# def Round():
#     n = input("是否進入淘汰賽(y:是,n:否):")
#     if n.lower() == "y":
#         b = int(input("取前幾名進入淘汰賽:"))


# 瑞士制配對

# 首輪
def DuelRound1():
    # 從資料庫中獲取參賽者名單
    select_query = """
        SELECT
            `id`,
            `Name`
        FROM
            `Now_Players`;
    """
    cursor.execute(select_query)
    players = cursor.fetchall()

    # 將參賽者名單洗牌
    random.shuffle(players)

    J = []
    if len(players) % 2 == 0:
        j = 0
        for i in range(int(len(players) / 2)):
            print(i + 1, ": ", players[j][1], players[j + 1][1])
            a = (players[j][1], players[j + 1][1])
            J.append(a)
            add_op0 = f"""INSERT INTO `id_{players[j][0]}` (`id`)
            VALUES ({players[j + 1][0]});"""
            add_op1 = f"""INSERT INTO `id_{players[j + 1][0]}` (`id`)
            VALUES ({players[j][0]});"""
            cursor.execute(add_op0)
            cursor.execute(add_op1)
            conn.commit()
            j += 2
    else:
        # 若參賽者數量為奇數，添加 Bye
        players.append((0, "Bye"))
        j = 0
        for i in range(int(len(players) / 2)):
            print(i + 1, ": ", players[j][1], players[j + 1][1])
            a = (players[j][1], players[j + 1][1])
            J.append(a)
            if i == int((len(players) / 2) - 1):
                break
            else:
                add_op0 = f"""INSERT INTO `id_{players[j][0]}` (`id`)
                VALUES ({players[j + 1][0]});"""
                add_op1 = f"""INSERT INTO `id_{players[j + 1][0]}` (`id`)
                VALUES ({players[j][0]});"""
                cursor.execute(add_op0)
                cursor.execute(add_op1)
                conn.commit()
            j += 2
    return J


## 輸入名單，輸出成一兩兩配對的組合


# 其他輪
def DuelRound():
    # 從資料庫中獲取參賽者名單按 Player_Rank 排序
    select_query = """
        SELECT
            `id`,
            `Name`
        FROM
            `Now_Players`
        ORDER BY
            `Player_Rank`;
    """
    cursor.execute(select_query)
    players = cursor.fetchall()

    J = []
    if len(players) % 2 == 0:
        j = 0
        for i in range(int(len(players) / 2)):
            a = (players[j][1], players[j + 1][1])

            # 檢查 `id_{}` 表中是否已經有了要加入的對手
            check_query_0 = f"SELECT COUNT(*) FROM `id_{players[j][0]}` WHERE `id` = {players[j + 1][0]};"
            cursor.execute(check_query_0)
            count_0 = cursor.fetchone()[0]

            check_query_1 = f"SELECT COUNT(*) FROM `id_{players[j + 1][0]}` WHERE `id` = {players[j][0]};"
            cursor.execute(check_query_1)
            count_1 = cursor.fetchone()[0]

            if count_0 == 0 and count_1 == 0:
                add_op0 = f"""INSERT INTO `id_{players[j][0]}` (`id`)
                VALUES ({players[j + 1][0]});"""
                add_op1 = f"""INSERT INTO `id_{players[j + 1][0]}` (`id`)
                VALUES ({players[j][0]});"""
                cursor.execute(add_op0)
                cursor.execute(add_op1)
                conn.commit()
                print(i + 1, ": ", players[j][1], players[j + 1][1])

            J.append(a)
            j += 2
    else:
        # 若參賽者數量為奇數，添加 Bye
        players.append((0, "Bye"))
        j = 0
        for i in range(int(len(players) / 2)):
            a = (players[j][1], players[j + 1][1])

            if i == int((len(players) / 2) - 1):
                print(i + 1, ": ", players[j][1], players[j + 1][1])
            else:
                # 檢查 `id_{}` 表中是否已經有了要加入的對手
                check_query = f"SELECT COUNT(*) FROM `id_{players[j][0]}` WHERE `id` = {players[j + 1][0]};"
                cursor.execute(check_query)
                count = cursor.fetchone()[0]

                if count == 0:
                    add_op0 = f"""INSERT INTO `id_{players[j][0]}` (`id`)
                    VALUES ({players[j + 1][0]});"""
                    add_op1 = f"""INSERT INTO `id_{players[j + 1][0]}` (`id`)
                    VALUES ({players[j][0]});"""
                    cursor.execute(add_op0)
                    cursor.execute(add_op1)
                    conn.commit()
                    print(i + 1, ": ", players[j][1], players[j + 1][1])
            J.append(a)
            j += 2

    return J


# 勝負
def Winner(J, cursor):
    for i in range(len(J)):
        while True:
            winner_name = str(input("請輸入第{}場勝利者名稱(平手輸入平手，雙敗輸入雙敗):".format(i + 1)))
            if winner_name == "平手":
                update_query = """
                    UPDATE `Now_Players`
                    SET `Point` = `Point` + %s
                    WHERE `Name` = %s;
                """
                cursor.execute(update_query, (WOL.T, J[i][0]))
                cursor.execute(update_query, (WOL.T, J[i][1]))
                break
            elif winner_name == "雙敗":
                update_query = """
                    UPDATE `Now_Players`
                    SET `Point` = `Point` + %s
                    WHERE `Name` = %s;
                """
                cursor.execute(update_query, (WOL.L, J[i][0]))
                cursor.execute(update_query, (WOL.L, J[i][1]))
                break
            # 更新資料庫中的 Point 欄位
            elif winner_name in (J[i][0], J[i][1]):
                update_query = """
                    UPDATE `Now_Players`
                    SET `Point` = `Point` + %s,
                        `Game_Win` = `Game_Win` + 1
                    WHERE `Name` = %s;
                """
                cursor.execute(update_query, (WOL.W, winner_name))
                break
            else:
                print("請輸入正確的名稱")

        update_query = """
            UPDATE `Now_Players`
            SET `Game` = `Game` + %s
            WHERE `Name` = %s;
        """
        cursor.execute(update_query, (1, J[i][0]))

        update_query = """
            UPDATE `Now_Players`
            SET `Game` = `Game` + %s
            WHERE `Name` = %s;
        """
        cursor.execute(update_query, (1, J[i][1]))

    conn.commit()


##輸入 組合 資訊 輸入勝利者 並在資訊中加入 勝利分

# OPW%


# show出當前排名
def Rank():
    select_query = """
        SELECT
            ROW_NUMBER() OVER (ORDER BY `Point` DESC, `OPW_percent` DESC, `OpOPW_percent` DESC) AS `Player_Rank`,
            `Name`,
            `id`,
            `Point`,
            `OPW_percent`,
            `OpOPW_percent`
        FROM
            `Now_Players`
        ORDER BY
            `Point` DESC, `OPW_percent` DESC, `OpOPW_percent` DESC;
    """
    cursor.execute(select_query)

    # 获取查询结果
    result = cursor.fetchall()

    # 获取表格列名
    columns = [i[0] for i in cursor.description]

    # 创建 PrettyTable 对象
    table = PrettyTable(columns)

    # 添加数据行
    for row in result:
        table.add_row(row)

    # 打印表格
    print(table)


# 淘汰制配對


### Test ###
a = "1"
while a == "1":
    __init__()
    Entrylist()
    rounds = int(input("請輸入瑞士輪輪次:"))
    if rounds > 1:
        A = DuelRound1()
        Winner(A, cursor)
        Renew()
        Renew_OPW()
        Renew_OPopW()
        Rank()
        for i in range(rounds - 1):
            A = DuelRound()
            Winner(A, cursor)
            Renew()
            Renew_OPW()
            Renew_OPopW()
            Rank()
    else:
        A = DuelRound1()
        Winner(A, cursor)
        Renew()
        Renew_OPW()
        Renew_OPopW()
        Rank()
    a = input("按下Enter結束，輸入1繼續:")

cursor.close()
conn.close()
