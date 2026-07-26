const fs = require('fs');
const path = require('path');

const arcDir = path.join(__dirname, 'arc');
const files = fs.readdirSync(arcDir).sort();

files.forEach((file, index) => {
    const ext = path.extname(file) || '.jpeg';
    const oldPath = path.join(arcDir, file);
    const newName = `memory_${index + 1}${ext}`;
    const newPath = path.join(arcDir, newName);
    fs.renameSync(oldPath, newPath);
    console.log(`Renamed ${file} -> ${newName}`);
});
console.log('Renaming completed successfully!');
