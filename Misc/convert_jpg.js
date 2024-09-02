const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

const inputFile = process.argv[2];
if (!inputFile) {
  console.error('Please provide an input file');
  process.exit(1);
}

const inputExt = path.extname(inputFile);
const baseName = path.basename(inputFile, inputExt);

// Convert to PNG
sharp(inputFile)
  .png()
  .toFile(`${baseName}.png`)
  .then(() => console.log('PNG conversion complete'))
  .catch((err) => console.error('Error converting to PNG:', err));

// Convert to ICO
sharp(inputFile)
  .resize(256, 256)
  .toFile(`${baseName}.ico`)
  .then(() => console.log('ICO conversion complete'))
  .catch((err) => console.error('Error converting to ICO:', err));
