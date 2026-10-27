const crypto = require('crypto');
const { AppError } = require('../errors');

function adminAuth(adminToken) {
    return (req, res, next) => {
        const provided = String(req.headers['x-admin-token'] || '');
        const expected = String(adminToken || '');
        const matches = expected.length > 0
            && provided.length === expected.length
            && crypto.timingSafeEqual(Buffer.from(provided), Buffer.from(expected));

        if (!matches) return next(new AppError(401, 'Não autorizado'));
        next();
    };
}

module.exports = adminAuth;
