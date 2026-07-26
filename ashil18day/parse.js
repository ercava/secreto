const fs = require('fs');
const path = require('path');

const csvPath = path.join(__dirname, 'mm - Sheet2.csv');
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
    let category = row[2].trim().toLowerCase();
    if (!name || !category) return null;

    if (name.toLowerCase() === 'barra' && message.toLowerCase() === 'video') {
        message = "Happy 18th Birthday Ashila! 🎉✨";
    }

    return { name, message, category };
}).filter(Boolean);

const memorandumData = data.map(item => {
    let media = null;
    let mediaType = 'image';
    const nameLower = item.name.toLowerCase();
    
    if (item.category === 'friends') {
        let imgPath = path.join(__dirname, 'friends', `${nameLower}.jpeg`);
        if (fs.existsSync(imgPath)) {
            media = `friends/${nameLower}.jpeg`;
        }
    } else if (item.category === 'os') {
        if (nameLower === 'barra') {
            media = 'os/barra.mp4';
            mediaType = 'video';
        } else {
            let imgPath = path.join(__dirname, 'os', `${nameLower}.jpeg`);
            if (fs.existsSync(imgPath)) {
                media = `os/${nameLower}.jpeg`;
            }
        }
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

// Arc / Scattered photos dataset
const arcDir = path.join(__dirname, 'arc');
let arcData = [];
if (fs.existsSync(arcDir)) {
    const arcFiles = fs.readdirSync(arcDir).filter(f => f.toLowerCase().endsWith('.jpeg') || f.toLowerCase().endsWith('.jpg') || f.toLowerCase().endsWith('.png')).sort((a, b) => {
        const numA = parseInt(a.replace(/[^0-9]/g, '')) || 0;
        const numB = parseInt(b.replace(/[^0-9]/g, '')) || 0;
        return numA - numB;
    });
    
    arcData = arcFiles.map((file, idx) => ({
        id: idx + 1,
        file: `arc/${file}`
    }));
}

const output = `// Auto-generated data file for Ashila
const memorandumData = ${JSON.stringify(memorandumData, null, 2)};
const arcData = ${JSON.stringify(arcData, null, 2)};
`;

fs.writeFileSync(path.join(__dirname, 'data.js'), output, 'utf-8');
console.log('Updated data.js for Ashila! Memorandum entries:', memorandumData.length, 'Arc entries:', arcData.length);
