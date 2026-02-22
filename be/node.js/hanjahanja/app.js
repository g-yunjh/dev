const express = require('express');
const fs = require('fs');
const path = require('path');
const favicon = require('serve-favicon');

const app = express();
const port = 3000;

// 정적 파일 서빙 설정
app.use(express.static(path.join(__dirname, 'public')));
// 파비콘 미들웨어 설정
app.use(favicon(path.join(__dirname, 'public/icons/favicon.ico')));

// JSON 파일에서 데이터 로드
const jsonDataPath = path.join(__dirname, 'hanja_data.json');
let hanjaData = {};

fs.readFile(jsonDataPath, 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading JSON file:', err);
        return;
    }
    hanjaData = JSON.parse(data);
});

// 정적 파일 서빙 설정
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.post('/process', (req, res) => {
    const inputHanja = req.body.hanja;
    let matchedMeanings = [];

    // 입력된 한자가 데이터에 있는지 검색
    for (let char of inputHanja) {
        if (hanjaData[char]) {
            matchedMeanings.push({ hanja: char, meaning: hanjaData[char] });
        }
    }

    res.json(matchedMeanings);
});

// 서버 시작
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});