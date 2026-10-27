const sqlite3 = require('sqlite3').verbose();

class Database {
    constructor(path) {
        this.connection = new sqlite3.Database(path);
        this.transactionQueue = Promise.resolve();
    }

    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.run(sql, params, function (err) {
                if (err) return reject(err);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
        });
    }

    // Serializa as transações: a conexão é única e BEGIN/COMMIT não podem se intercalar.
    transaction(work) {
        const execution = this.transactionQueue.then(async () => {
            await this.run('BEGIN');
            try {
                const result = await work();
                await this.run('COMMIT');
                return result;
            } catch (err) {
                await this.run('ROLLBACK');
                throw err;
            }
        });
        this.transactionQueue = execution.catch(() => {});
        return execution;
    }
}

module.exports = Database;
