const path = require('path');
const multer = require('multer');

const uploadDir = path.join(__dirname, '../../uploads');

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => cb(null, file.originalname.replace(/\s/g, '_')),
});

const upload = multer({ storage });

module.exports = upload;
