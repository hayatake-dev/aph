-- 既存のテーブルがあれば削除 (開発時にテーブル構造を変更する場合に便利)
-- DROP TABLE IF EXISTS reservations;
-- DROP TABLE IF EXISTS rooms;

-- ユーザー用テーブル
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- 部屋テーブル
CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    capacity INT NOT NULL,
    price INT NOT NULL,
    img VARCHAR(255)
);

-- 予約テーブル
CREATE TABLE reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    room_id INT NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100),
    checkin DATE NOT NULL,
    checkout DATE NOT NULL,
    people INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- 3. 初期データの挿入
-- アプリケーションの起動時に一度だけ実行され、部屋のマスターデータを作成
INSERT INTO rooms (id, name, type, capacity, price, img) VALUES
(1, 'スタンダードプラン', 'シングル', 1, 8500, 'img/room1.jpg'),
(2, 'プレミアムプラン', 'ダブル', 2, 12000, 'img/room2.jpg'),
(3, 'スイートプラン', 'ツイン', 2, 18000, 'img/room3.jpg');

-- ユーザー情報もデータベースに保存する場合は、usersテーブルを追加します
-- CREATE TABLE users (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     username TEXT UNIQUE NOT NULL,
--     password TEXT NOT NULL -- 実際にはハッシュ化されたパスワード
-- );

