#!/usr/bin/env node

/**
 * Главный файл для автоматического сбора cookies
 */
const CookieExtractor = require('./cookie_extractor.js');

// Главная функция
async function main() {
    let extractor = null;
    
    try {
        console.log('🍪 Запуск автоматического сборщика cookies...');
        
        extractor = new CookieExtractor();
        
        // Инициализируем браузер
        await extractor.init();
        
        // Собираем cookies
        const cookies = await extractor.extractCookies();
        
        // Валидируем cookies
        const validation = extractor.validateCookies();
        
        // Сохраняем cookies
        const cookies_file = '/app/docs/auto_extracted_cookies.json';
        await extractor.saveCookies(cookies_file);
        
        // Выводим результат с защитой от null/undefined validation
        const safeValidation = validation || {
            isValid: false,
            errors: [],
            warnings: [],
            criticalCookies: {}
        };
        
        const result = {
            success: true,
            cookies: cookies,
            validation: safeValidation,
            message: 'Cookies успешно собраны автоматически',
            stats: {
                total_cookies: Object.keys(cookies || {}).length,
                critical_cookies: Object.keys(safeValidation.criticalCookies || {}).length,
                isValid: safeValidation.isValid || false,
                errors: (safeValidation.errors || []).length,
                warnings: (safeValidation.warnings || []).length
            }
        };
        
        console.log(JSON.stringify(result));
        
    } catch (error) {
        console.log(JSON.stringify({ 
            success: false, 
            error: error.message,
            message: 'Ошибка автоматического сбора cookies'
        }));
    } finally {
        if (extractor) {
            await extractor.close();
        }
    }
}

// Запуск
if (require.main === module) {
    main().catch(error => {
        console.log(JSON.stringify({ 
            success: false, 
            error: error.message,
            message: 'Критическая ошибка cookie extractor'
        }));
        process.exit(1);
    });
}

module.exports = main;
