-- Create Channels table
CREATE TABLE Channels (
    channel_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    creation_date DATE,
    total_subscribers INT,
    total_view_count BIGINT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Videos table
CREATE TABLE Videos (
    video_id VARCHAR(255) PRIMARY KEY,
    channel_id VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    duration INT,
    upload_date DATE,
    view_count BIGINT,
    like_count INT,
    dislike_count INT,
    description TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
);

-- Create Playlists table
CREATE TABLE Playlists (
    playlist_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    creator_id VARCHAR(255),
    creation_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Persons table
CREATE TABLE Persons (
    person_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    channel_id VARCHAR(255),
    role VARCHAR(255),
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
);

-- Create Comments table
CREATE TABLE Comments (
    comment_id VARCHAR(255) PRIMARY KEY,
    video_id VARCHAR(255),
    author_id VARCHAR(255),
    text TEXT NOT NULL,
    comment_date DATE,
    like_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES Videos(video_id),
    FOREIGN KEY (author_id) REFERENCES Persons(person_id)
);

