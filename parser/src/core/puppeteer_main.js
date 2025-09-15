#!/usr/bin/env node

/**
 * Главный файл для вызова функций Puppeteer парсера
 */
const PuppeteerParser = require('./puppeteer_parser.js');

// Парсинг аргументов командной строки
function parseArgs() {
    const args = process.argv.slice(2);
    const parsed = {};
    const fs = require('fs');
    
    let i = 0;
    
    // Обрабатываем первый аргумент как команду, если он не начинается с '--'
    if (args.length > 0 && !args[0].startsWith('--')) {
        parsed.command = args[0];
        parsed._ = args[0];
        i = 1;
    }
    
    // Обрабатываем остальные аргументы
    while (i < args.length) {
        const arg = args[i];
        
        if (arg.startsWith('--')) {
            const key = arg.substring(2);
            const nextArg = args[i + 1];
            
            // Проверяем, есть ли следующий аргумент и не является ли он флагом
            if (nextArg && !nextArg.startsWith('--')) {
                // Следующий аргумент - значение
                const value = nextArg;
                
                // Если значение - путь к JSON файлу, читаем его
                if (value.endsWith('.json') && fs.existsSync(value)) {
                    try {
                        parsed[key] = JSON.parse(fs.readFileSync(value, 'utf8'));
                    } catch (e) {
                        parsed[key] = value;
                    }
                } else {
                    parsed[key] = value;
                }
                i += 2; // Пропускаем и ключ, и значение
            } else {
                // Следующего аргумента нет или он тоже флаг - это булевый флаг
                parsed[key] = true;
                i += 1; // Пропускаем только ключ
            }
        } else {
            // Аргумент без '--' - пропускаем (возможно, позиционный аргумент)
            i += 1;
        }
    }
    
    return parsed;
}

// Главная функция
async function main() {
    const args = parseArgs();
    const command = args.command || args._ || 'help';
    
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
