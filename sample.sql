
CREATE TABLE Users(
    userId INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(34) NOT NULL UNIQUE,
    firstName TEXT NOT NULL,
    lastName TEXT,
    dob DATE NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    gender CHAR(1) NOT NULL,
    createdAt TIMESTAMP NOT NULL
);

CREATE TABLE Questions(
    questionId INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    createdAt TIMESTAMP NOT NULL,
    image BLOB,
    userId INTEGER NOT NULL,
    FOREIGN KEY(userId) REFERENCES Users(userId)
);

CREATE TABLE REPLIES(
    replyId INTEGER PRIMARY KEY,
    message TEXT NOT NULL,
    createdAt TIMESTAMP NOT NULL,
    userId INTEGER NOT NULL,
    questionId INTEGER NOT NULL,
    FOREIGN KEY(userId) REFERENCES Users(userId),
    FOREIGN KEY(questionId) REFERENCES Questions(questionId)
);

CREATE TABLE REACTIONS(
    reactionId INTEGER PRIMARY KEY,
    reactionType CHAR(1) NOT NULL,
    createdAt TIMESTAMP NOT NULL,
    userId INTEGER NOT NULL,
    questionId INTEGER NOT NULL,
    FOREIGN KEY(userId) REFERENCES Users(userId),
    FOREIGN KEY(questionId) REFERENCES Questions(questionId)
);

CREATE TABLE HASHTAGS(
    hashtagId INTEGER PRIMARY KEY,
    hashtag VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE FILTERBYHASHTAG(
    questionId INTEGER NOT NULL,
    hashtagId INTEGER NOT NULL,
    FOREIGN KEY(questionId) REFERENCES Questions(questionId),
    FOREIGN KEY(hashtagId) REFERENCES HASHTAGS(hashtagId)
);





ALTER TABLE USERS ADD COLUMN hashedPassword TEXT NOT NULL;


INSERT INTO Users(email, firstName, lastName, dob, phone,gender,createdAt,hashedPassword) VALUES (
    "bhavish@gmail.com",
    "Bhavish",
    "A",
    "31-07-2001",
    "9353059824",
    "M",


);