const crypto = require('crypto');
const { promisify } = require('util');

const scrypt = promisify(crypto.scrypt);
const SALT_BYTES = 16;
const KEY_LENGTH = 64;

async function hash(password) {
    const salt = crypto.randomBytes(SALT_BYTES).toString('hex');
    const derived = await scrypt(password, salt, KEY_LENGTH);
    return `${salt}:${derived.toString('hex')}`;
}

async function verify(password, stored) {
    const [salt, key] = stored.split(':');
    const derived = await scrypt(password, salt, KEY_LENGTH);
    return crypto.timingSafeEqual(derived, Buffer.from(key, 'hex'));
}

module.exports = { hash, verify };
