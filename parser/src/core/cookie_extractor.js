/**
 * Автоматический сборщик cookies для kad.arbitr.ru
 * Использует Puppeteer для автоматического получения всех необходимых cookies
 */
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');

// Добавляем stealth плагин
puppeteer.use(StealthPlugin());

class CookieExtractor {
    constructor() {
        this.browser = null;
        this.page = null;
        this.extracted_cookies = {};
    }

    /**
     * Получение дат для API запроса с валидацией
     */
    getApiDates(dateFrom = null, dateTo = null) {
        const today = new Date();
        const defaultFrom = new Date(today.getFullYear(), 0, 1); // 1 января текущего года
        const defaultTo = today;

        // Валидация и форматирование дат
        const formatDate = (date) => {
            if (!date) return null;
            
            const d = new Date(date);
            if (isNaN(d.getTime())) {
                console.warn(`⚠️ Некорректная дата: ${date}, используется значение по умолчанию`);
                return null;
            }
            
            return d.toISOString().split('T')[0]; // YYYY-MM-DD формат
        };

        const fromDate = formatDate(dateFrom) || formatDate(defaultFrom);
        const toDate = formatDate(dateTo) || formatDate(defaultTo);

        // Дополнительная валидация: fromDate не должна быть позже toDate
        if (fromDate && toDate && new Date(fromDate) > new Date(toDate)) {
            console.warn('⚠️ DateFrom позже DateTo, меняем местами');
            return { DateFrom: toDate, DateTo: fromDate };
        }

        return { DateFrom: fromDate, DateTo: toDate };
    }

    /**
     * Инициализация браузера
     */
    async init() {
        console.log('🚀 Запуск браузера для сбора cookies...');
        
        this.browser = await puppeteer.launch({
            headless: 'new', // Используем headless режим для Docker
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--window-size=1920,1080'
            ]
        });

        this.page = await this.browser.newPage();
        
        // Настраиваем viewport
        await this.page.setViewport({ width: 1920, height: 1080 });
        
        // Устанавливаем User-Agent
        await this.page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        
        console.log('✅ Браузер запущен успешно');
    }

    /**
     * Автоматический сбор cookies с kad.arbitr.ru
     */
    async extractCookies() {
        try {
            console.log('🍪 Начинаем автоматический сбор cookies...');
            
            // Шаг 1: Переходим на главную страницу
            console.log('📄 Переходим на kad.arbitr.ru...');
            await this.page.goto('https://kad.arbitr.ru/', { 
                waitUntil: 'networkidle2',
                timeout: 30000 
            });

            // Ждем полной загрузки страницы
            await this.page.waitForTimeout(3000);

            // Шаг 2: Проверяем наличие anti-bot защиты
            console.log('🔍 Проверяем anti-bot защиту...');
            
            // Ищем элементы, указывающие на anti-bot защиту
            const hasAntiBot = await this.page.evaluate(() => {
                // Проверяем различные признаки anti-bot защиты
                const indicators = [
                    document.querySelector('[data-testid="captcha"]'),
                    document.querySelector('.captcha'),
                    document.querySelector('[class*="captcha"]'),
                    document.querySelector('[id*="captcha"]'),
                    document.querySelector('iframe[src*="captcha"]'),
                    document.querySelector('iframe[src*="recaptcha"]'),
                    document.querySelector('[class*="ddos"]'),
                    document.querySelector('[id*="ddos"]')
                ];
                
                return indicators.some(indicator => indicator !== null);
            });

            if (hasAntiBot) {
                console.log('⚠️ Обнаружена anti-bot защита, ожидаем...');
                // Ждем больше времени для прохождения защиты
                await this.page.waitForTimeout(5000);
            }

            // Шаг 3: Пытаемся выполнить поиск для активации всех cookies
            console.log('🔍 Выполняем тестовый поиск для активации cookies...');
            
            try {
                // Ищем форму поиска и заполняем её
                await this.page.waitForSelector('input[type="text"], input[type="search"], .search-input', { timeout: 10000 });
                
                // Заполняем поисковое поле
                await this.page.type('input[type="text"], input[type="search"], .search-input', 'тест');
                
                // Нажимаем кнопку поиска
                await this.page.click('button[type="submit"], .search-button, [class*="search"] button');
                
                // Ждем загрузки результатов
                await this.page.waitForTimeout(3000);
                
            } catch (error) {
                console.error('⚠️ Не удалось выполнить поиск, продолжаем...', {
                    error: error.message,
                    stack: error.stack,
                    context: 'test_search_execution'
                });
            }

            // Шаг 4: Собираем все cookies
            console.log('🍪 Собираем cookies...');
            const cookies = await this.page.cookies();
            
            // Конвертируем cookies в простой объект
            this.extracted_cookies = {};
            for (const cookie of cookies) {
                this.extracted_cookies[cookie.name] = cookie.value;
            }

            // Шаг 5: Проверяем наличие критически важных cookies
            const requiredCookies = ['pr_fp', 'wasm', 'PHPSESSID', 'ASP.NET_SessionId'];
            const foundRequired = [];
            const missingRequired = [];

            for (const cookieName of requiredCookies) {
                if (this.extracted_cookies[cookieName]) {
                    foundRequired.push(cookieName);
                } else {
                    missingRequired.push(cookieName);
                }
            }

            console.log(`✅ Найдено cookies: ${Object.keys(this.extracted_cookies).length}`);
            console.log(`✅ Критически важные cookies: ${foundRequired.join(', ')}`);
            
            if (missingRequired.length > 0) {
                console.log(`⚠️ Отсутствуют важные cookies: ${missingRequired.join(', ')}`);
            }

            // Шаг 6: Дополнительная активация cookies через API запрос
            console.log('🔄 Активируем cookies через API запрос...');
            
            try {
                // Получаем валидированные даты
                const dates = this.getApiDates();
                console.log(`📅 Используем даты: ${dates.DateFrom} - ${dates.DateTo}`);
                
                // Выполняем тестовый API запрос
                const apiResponse = await this.page.evaluate(async (requestDates) => {
                    try {
                        const response = await fetch('https://kad.arbitr.ru/Kad/SearchInstances', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json; charset=UTF-8',
                                'Accept': 'application/json, text/javascript, */*; q=0.01',
                                'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                                'Origin': 'https://kad.arbitr.ru',
                                'Referer': 'https://kad.arbitr.ru/',
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            body: JSON.stringify({
                                Page: 1,
                                Count: 1,
                                Courts: [],
                                DateFrom: requestDates.DateFrom,
                                DateTo: requestDates.DateTo,
                                Sides: [],
                                Judges: [],
                                CaseNumbers: [],
                                WithVKSInstances: false,
                                ReasonIds: [],
                                CaseTypeIds: [],
                                CaseCategoryIds: [],
                                InstanceIds: [],
                                RegionIds: [],
                                DateType: 0
                            })
                        });
                        
                        return {
                            status: response.status,
                            success: response.ok
                        };
                    } catch (error) {
                        return {
                            status: 'error',
                            success: false,
                            error: error.message
                        };
                    }
                }, dates);

                if (apiResponse.success) {
                    console.log('✅ API запрос успешен - cookies активны');
                } else {
                    console.log(`⚠️ API запрос неуспешен: ${apiResponse.status}`);
                }

                // Собираем cookies еще раз после API запроса
                const updatedCookies = await this.page.cookies();
                this.extracted_cookies = {};
                for (const cookie of updatedCookies) {
                    this.extracted_cookies[cookie.name] = cookie.value;
                }

                console.log(`✅ Обновлено cookies: ${Object.keys(this.extracted_cookies).length}`);

            } catch (error) {
                console.log(`⚠️ Ошибка API запроса: ${error.message}`);
            }

            return this.extracted_cookies;

        } catch (error) {
            console.error('❌ Ошибка сбора cookies:', error.message);
            throw error;
        }
    }

    /**
     * Сохранение cookies в файл
     */
    async saveCookies(filePath) {
        try {
            console.log(`💾 Сохраняем cookies в файл: ${filePath}`);
            
            // Создаем директорию если не существует
            const dir = path.dirname(filePath);
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }

            // Сохраняем cookies
            fs.writeFileSync(filePath, JSON.stringify(this.extracted_cookies, null, 2), 'utf8');
            
            console.log('✅ Cookies сохранены успешно');
            return true;

        } catch (error) {
            console.error('❌ Ошибка сохранения cookies:', error.message);
            return false;
        }
    }

    /**
     * Валидация cookies
     */
    validateCookies() {
        const validation = {
            isValid: true,
            errors: [],
            warnings: [],
            foundCookies: Object.keys(this.extracted_cookies),
            criticalCookies: {}
        };

        // Проверяем критически важные cookies
        const criticalCookies = {
            'pr_fp': 'Основной fingerprint cookie',
            'wasm': 'WebAssembly токен (опциональный)',
            'PHPSESSID': 'PHP сессия (опциональный)',
            'ASP.NET_SessionId': 'ASP.NET сессия (опциональный)'
        };

        for (const [cookieName, description] of Object.entries(criticalCookies)) {
            if (this.extracted_cookies[cookieName]) {
                const cookieValue = this.extracted_cookies[cookieName] || '';
                validation.criticalCookies[cookieName] = {
                    found: true,
                    description: description,
                    value: String(cookieValue).substring(0, 20) + '...'
                };
            } else {
                if (cookieName === 'pr_fp') {
                    validation.isValid = false;
                    validation.errors.push(`Отсутствует критически важный cookie: ${cookieName} (${description})`);
                } else {
                    validation.warnings.push(`Отсутствует опциональный cookie: ${cookieName} (${description})`);
                }
            }
        }

        // Проверяем общее количество cookies
        const totalCookies = Object.keys(this.extracted_cookies).length;
        if (totalCookies < 5) {
            validation.warnings.push(`Мало cookies (${totalCookies}), возможно anti-bot защита активна`);
        }

        return validation;
    }

    /**
     * Закрытие браузера
     */
    async close() {
        if (this.browser) {
            await this.browser.close();
            console.log('🔒 Браузер закрыт');
        }
    }
}

module.exports = CookieExtractor;
