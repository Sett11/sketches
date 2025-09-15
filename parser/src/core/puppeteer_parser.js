/**
 * Puppeteer парсер для kad.arbitr.ru с stealth плагином
 */
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');

// Добавляем stealth плагин
puppeteer.use(StealthPlugin());

class PuppeteerParser {
    constructor(options = {}) {
        this.browser = null;
        this.page = null;
        this.cookies = null;
        
        // Настраиваемый путь к директории docs
        // Приоритет: options.docsDir -> process.env.DOCS_DIR -> fallback
        this.docsDir = options.docsDir || 
                      process.env.DOCS_DIR || 
                      path.join(process.cwd(), 'docs');
        
        console.log(`📁 Директория для документов: ${this.docsDir}`);
    }

    /**
     * Инициализация браузера
     */
    async init() {
        console.log('🚀 Запуск браузера с stealth режимом...');
        
        this.browser = await puppeteer.launch({
            headless: 'new', // Используем новый headless режим
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
                '--disable-renderer-backgrounding'
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
     * Загрузка cookies из JSON файла
     */
    async loadCookies(cookiesPath) {
        try {
            if (!fs.existsSync(cookiesPath)) {
                throw new Error(`Файл cookies не найден: ${cookiesPath}`);
            }

            const cookiesData = JSON.parse(fs.readFileSync(cookiesPath, 'utf8'));
            
            // Конвертируем cookies в формат Puppeteer
            const puppeteerCookies = Object.entries(cookiesData).map(([name, value]) => ({
                name,
                value,
                domain: '.arbitr.ru',
                path: '/',
                httpOnly: false,
                secure: true,
                sameSite: 'Lax'
            }));

            // Устанавливаем cookies
            await this.page.setCookie(...puppeteerCookies);
            
            this.cookies = cookiesData;
            console.log(`✅ Загружено ${Object.keys(cookiesData).length} cookies`);
            
            return true;
        } catch (error) {
            console.error('❌ Ошибка загрузки cookies:', error.message);
            return false;
        }
    }

    /**
     * Поиск документов через API
     */
    async searchDocuments(searchParams) {
        try {
            console.log('🔍 Выполняем поиск документов...');
            
            // Сначала заходим на главную страницу для инициализации сессии
            await this.page.goto('https://kad.arbitr.ru/', { 
                waitUntil: 'networkidle2',
                timeout: 30000 
            });

            // Ждем немного для полной загрузки
            await this.page.waitForTimeout(2000);

            // Выполняем POST запрос к API
            const response = await this.page.evaluate(async (params) => {
                const response = await fetch('https://kad.arbitr.ru/Kad/SearchInstances', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json; charset=UTF-8',
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Origin': 'https://kad.arbitr.ru',
                        'Referer': 'https://kad.arbitr.ru/',
                        'X-Requested-With': 'XMLHttpRequest',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin'
                    },
                    body: JSON.stringify(params)
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();
            }, searchParams);

            console.log('✅ Поиск выполнен успешно');
            return response;

        } catch (error) {
            console.error('❌ Ошибка поиска документов:', error.message);
            throw error;
        }
    }

    /**
     * Скачивание PDF документа
     */
    async downloadPDF(pdfUrl, filename) {
        try {
            console.log(`📄 Скачиваем PDF: ${filename}`);
            
            // Переходим к PDF
            const response = await this.page.goto(pdfUrl, { 
                waitUntil: 'networkidle2',
                timeout: 30000 
            });

            if (!response.ok()) {
                throw new Error(`Ошибка загрузки PDF: ${response.status()}`);
            }

            // Получаем содержимое PDF
            const pdfBuffer = await response.buffer();
            
            // Сохраняем файл
            if (!fs.existsSync(this.docsDir)) {
                fs.mkdirSync(this.docsDir, { recursive: true });
            }

            const filepath = path.join(this.docsDir, filename);
            fs.writeFileSync(filepath, pdfBuffer);
            
            console.log(`✅ PDF сохранен: ${filepath}`);
            return filepath;

        } catch (error) {
            console.error(`❌ Ошибка скачивания PDF ${filename}:`, error.message);
            return null;
        }
    }

    /**
     * Обработка диапазона дат
     */
    async processDateRange(startDate, endDate, maxPages = 40) {
        const results = [];
        
        if (!fs.existsSync(this.docsDir)) {
            fs.mkdirSync(this.docsDir, { recursive: true });
        }

        let currentDate = new Date(startDate);
        const endDateObj = new Date(endDate);

        while (currentDate <= endDateObj) {
            const nextDate = new Date(currentDate);
            nextDate.setDate(nextDate.getDate() + 2); // Шаг 2 дня

            console.log(`📅 Обрабатываем период: ${currentDate.toISOString().split('T')[0]} - ${nextDate.toISOString().split('T')[0]}`);

            try {
                // Создаем параметры поиска
                const searchParams = {
                    Page: 1,
                    Count: 25,
                    Courts: [],
                    DateFrom: currentDate.toISOString().split('T')[0],
                    DateTo: nextDate.toISOString().split('T')[0],
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
                };

                // Обрабатываем страницы
                for (let page = 1; page <= maxPages; page++) {
                    searchParams.Page = page;
                    
                    const response = await this.searchDocuments(searchParams);
                    
                    if (!response || !response.data || response.data.length === 0) {
                        console.log(`📄 Страница ${page} пустая, завершаем`);
                        break;
                    }

                    console.log(`📄 Обрабатываем страницу ${page}, найдено документов: ${response.data.length}`);

                    // Фильтруем и скачиваем документы
                    for (const doc of response.data) {
                        // Простая фильтрация по ключевым словам
                        const text = `${doc.CaseNumber || ''} ${doc.Title || ''}`.toLowerCase();
                        
                        // Исключаем ненужные документы
                        const excludeKeywords = ['перенос', 'отложение', 'назначение', 'включение в реестр'];
                        const shouldExclude = excludeKeywords.some(keyword => text.includes(keyword));
                        
                        if (shouldExclude) {
                            console.log(`⏭️ Пропускаем: ${doc.Title}`);
                            continue;
                        }

                        // Включаем нужные документы
                        const includeKeywords = ['решение', 'кассация', 'определение'];
                        const shouldInclude = includeKeywords.some(keyword => text.includes(keyword));
                        
                        if (shouldInclude && doc.DocumentUrl) {
                            const filename = `${doc.CaseNumber || 'unknown'}_${Date.now()}.pdf`;
                            const filepath = await this.downloadPDF(doc.DocumentUrl, filename);
                            
                            if (filepath) {
                                results.push({
                                    caseNumber: doc.CaseNumber,
                                    title: doc.Title,
                                    date: doc.Date,
                                    url: doc.DocumentUrl,
                                    filepath: filepath
                                });
                            }

                            // Задержка между скачиваниями
                            await this.page.waitForTimeout(1000);
                        }
                    }

                    // Задержка между страницами
                    await this.page.waitForTimeout(2000);
                }

            } catch (error) {
                console.error('❌ Ошибка обработки периода:', error.message);
            }

            currentDate = nextDate;
        }

        // Сохраняем метаданные
        const metadataPath = path.join(this.docsDir, 'metadata.json');
        fs.writeFileSync(metadataPath, JSON.stringify({
            processed_at: new Date().toISOString(),
            total_documents: results.length,
            documents: results
        }, null, 2));

        console.log(`✅ Обработка завершена. Скачано документов: ${results.length}`);
        return results;
    }

    /**
     * Получение статистики
     */
    getStats() {
        try {
            const metadataPath = path.join(this.docsDir, 'metadata.json');
            
            if (!fs.existsSync(metadataPath)) {
                return { total_documents: 0, last_update: null };
            }

            const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
            return {
                total_documents: metadata.total_documents || 0,
                last_update: metadata.processed_at || null
            };

        } catch (error) {
            console.error('❌ Ошибка получения статистики:', error.message);
            return { total_documents: 0, last_update: null };
        }
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

module.exports = PuppeteerParser;
