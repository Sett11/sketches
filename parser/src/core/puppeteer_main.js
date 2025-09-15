#!/usr/bin/env node

/**
 * Главный файл для вызова функций Puppeteer парсера
 */
const PuppeteerParser = require('./puppeteer_parser.js');

// Парсинг аргументов командной строки
function parseArgs() {
    const args = process.argv.slice(2);
    const parsed = {};
    
    for (let i = 0; i < args.length; i += 2) {
        if (args[i].startsWith('--')) {
            const key = args[i].substring(2);
            const value = args[i + 1];
            
            // Если значение - путь к JSON файлу, читаем его
            if (value && value.endsWith('.json') && require('fs').existsSync(value)) {
                try {
                    parsed[key] = JSON.parse(require('fs').readFileSync(value, 'utf8'));
                } catch (e) {
                    parsed[key] = value;
                }
            } else {
                parsed[key] = value;
            }
        }
    }
    
    return parsed;
}

// Главная функция
async function main() {
    const args = parseArgs();
    const command = args._ || args[0] || 'help';
    
    let parser = null;
    
    try {
        switch (command) {
            case 'init':
                parser = new PuppeteerParser();
                await parser.init();
                console.log(JSON.stringify({ success: true, message: 'Браузер инициализирован' }));
                break;
                
            case 'loadCookies':
                parser = new PuppeteerParser();
                await parser.init();
                
                if (args.cookies_file) {
                    const success = await parser.loadCookies(args.cookies_file);
                    console.log(JSON.stringify({ 
                        success: success, 
                        message: success ? 'Cookies загружены' : 'Ошибка загрузки cookies' 
                    }));
                } else {
                    console.log(JSON.stringify({ 
                        success: false, 
                        error: 'Не указан файл cookies' 
                    }));
                }
                break;
                
            case 'searchDocuments':
                parser = new PuppeteerParser();
                await parser.init();
                
                if (args.cookies_file) {
                    await parser.loadCookies(args.cookies_file);
                }
                
                if (args.params) {
                    const result = await parser.searchDocuments(args.params);
                    console.log(JSON.stringify({ 
                        success: true, 
                        data: result 
                    }));
                } else {
                    console.log(JSON.stringify({ 
                        success: false, 
                        error: 'Не указаны параметры поиска' 
                    }));
                }
                break;
                
            case 'processDateRange':
                parser = new PuppeteerParser();
                await parser.init();
                
                if (args.cookies_file) {
                    await parser.loadCookies(args.cookies_file);
                }
                
                if (args.start_date && args.end_date) {
                    const maxPages = parseInt(args.max_pages) || 40;
                    const result = await parser.processDateRange(
                        args.start_date, 
                        args.end_date, 
                        maxPages
                    );
                    console.log(JSON.stringify({ 
                        success: true, 
                        data: result 
                    }));
                } else {
                    console.log(JSON.stringify({ 
                        success: false, 
                        error: 'Не указаны даты начала и окончания' 
                    }));
                }
                break;
                
            case 'getStats':
                parser = new PuppeteerParser();
                const stats = parser.getStats();
                console.log(JSON.stringify({ 
                    success: true, 
                    data: stats 
                }));
                break;
                
            case 'close':
                parser = new PuppeteerParser();
                await parser.close();
                console.log(JSON.stringify({ 
                    success: true, 
                    message: 'Браузер закрыт' 
                }));
                break;
                
            default:
                console.log(JSON.stringify({ 
                    success: false, 
                    error: `Неизвестная команда: ${command}` 
                }));
                break;
        }
        
    } catch (error) {
        console.log(JSON.stringify({ 
            success: false, 
            error: error.message 
        }));
    } finally {
        if (parser && parser.browser) {
            await parser.close();
        }
    }
}

// Запуск
if (require.main === module) {
    main().catch(error => {
        console.log(JSON.stringify({ 
            success: false, 
            error: error.message 
        }));
        process.exit(1);
    });
}

module.exports = main;
