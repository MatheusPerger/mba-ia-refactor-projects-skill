const logger = require('../logger');

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    if (err.statusCode) return res.status(err.statusCode).send(err.message);

    logger.error(err.stack || String(err));
    res.status(500).send('Erro interno');
}

module.exports = errorHandler;
