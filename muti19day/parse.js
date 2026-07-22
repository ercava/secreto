const fs = require('fs');
const path = require('path');

const csvPath = path.join(__dirname, 'mm - Sheet1.csv');
const csvContent = fs.readFileSync(csvPath, 'utf-8');

function parseCSV(text) {
    const lines = [];
    let row = [""];
    let inQuotes = false;
    
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        const nextChar = text[i + 1];
        
        if (char === '"') {
            if (inQuotes && nextChar === '"') {
                row[row.length - 1] += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        } else if (char === ',' && !inQuotes) {
            row.push("");
        } else if ((char === '\r' || char === '\n') && !inQuotes) {
            if (char === '\r' && nextChar === '\n') i++;
            lines.push(row);
            row = [""];
        } else {
            row[row.length - 1] += char;
        }
    }
    if (row.length > 1 || row[0] !== "") lines.push(row);
    return lines;
}

function getInitials(name) {
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
}

const parsed = parseCSV(csvContent);
const data = parsed.map(row => {
    if (row.length < 3) return null;
    let name = row[0].trim();
    let message = row[1].trim();
    let category = row[2].trim();
    if (!name || !category) return null;

    if (name.toLowerCase() === 'thia') {
        category = 'bio';
    }

    // Add explicit letter message for Kei
    if (name.toLowerCase() === 'kei') {
        message = `makan sambal rasa avocado
minum cireng latte warna green
selamat bertambah umur cristiano mutiaronaldo
panjang umur sehat bahagia selalu amiin`;
    }

    return { name, message, category };
}).filter(Boolean);

const resolvedData = data.map(item => {
    let media = null;
    let mediaType = 'image';
    const nameLower = item.name.toLowerCase();
    
    if (item.category === 'friends') {
        let imgName = item.name;
        if (nameLower === 'raqiqa') imgName = 'raqi';
        if (nameLower === 'sovaa') imgName = 'sova';
        media = `friends/${imgName}.jpeg`;
    } else if (item.category === 'kebsen') {
        if (nameLower === 'kak naura') {
            media = 'kebsen/kakNaura.mp4';
            mediaType = 'video';
        } else {
            media = `kebsen/${item.name}.jpeg`;
        }
    } else if (item.category === 'bio') {
        media = `bio/${item.name}.jpeg`;
    }
    
    return {
        name: item.name,
        initials: getInitials(item.name),
        message: item.message,
        category: item.category,
        media,
        mediaType
    };
});

const zLetterText = fs.readFileSync(path.join(__dirname, 'z', 'letters.txt'), 'utf-8').trim();
const zData = {
    message: zLetterText,
    pic: 'z/pic.jpeg',
    sign: 'z/sign.png'
};

const output = `// Auto-generated data file
const memorandumData = ${JSON.stringify(resolvedData, null, 2)};
const zLetterData = ${JSON.stringify(zData, null, 2)};
`;

fs.writeFileSync(path.join(__dirname, 'data.js'), output, 'utf-8');
console.log('Updated data.js with Kei message! Total entries:', resolvedData.length);
