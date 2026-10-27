const format = (level, message) => `${new Date().toISOString()} [${level}] ${message}`;

module.exports = {
    info: (message) => console.log(format('INFO', message)),
    error: (message) => console.error(format('ERROR', message))
};
