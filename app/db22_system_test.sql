SELECT 1;
-- テスト用データの挿入スクリプト
-- 1. accounts テーブルの作成（もし存在しない場合）
CREATE TABLE IF NOT EXISTS accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);



-- アカウントのテストデータ
INSERT INTO accounts (username, password_hash, email) VALUES
('testuser1', 'hashed_password_1', 'test1@example.com'),
('testuser2', 'hashed_password_2', 'test2@example.com'),
('admin', 'hashed_admin_password', 'admin@example.com');

-- 予約のテストデータ
INSERT INTO reservations (room_id, room_name, name, email, checkin, checkout, people) VALUES
(1, 'スタンダードプラン', '山田太郎', 'yamada@example.com', '2025-12-20', '2025-12-21', 1),
(2, 'プレミアムプラン', '鈴木花子', 'suzuki@example.com', '2025-12-22', '2025-12-23', 2),
(3, 'スイートプラン', '佐藤次郎', 'sato@example.com', '2025-12-24', '2025-12-25', 2);

-- 追加の部屋データ（必要に応じて）
INSERT INTO rooms (id, name, type, capacity, price, img) VALUES
(4, 'エグゼクティブプラン', 'ダブル', 2, 22000, 'img/room4.jpg'),
(5, 'ファミリープラン', 'ツイン', 4, 25000, 'img/room5.jpg'),
(6, 'デラックスプラン', 'シングル', 1, 15000, 'img/room6.jpg');
