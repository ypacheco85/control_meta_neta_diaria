// Obtener todos los elementos del DOM
const inputs = {
    mpg: document.getElementById('mpg'),
    gasPrice: document.getElementById('gas-price'),
    metaNeta: document.getElementById('meta-neta'),
    uberEarnings: document.getElementById('uber-earnings'),
    lyftEarnings: document.getElementById('lyft-earnings'),
    cashTips: document.getElementById('cash-tips'),
    odoStart: document.getElementById('odo-start'),
    odoEnd: document.getElementById('odo-end'),
    foodCost: document.getElementById('food-cost'),
    miscCost: document.getElementById('misc-cost')
};

// Array para almacenar gastos adicionales
let additionalExpenses = [];

const outputs = {
    totalGross: document.getElementById('total-gross'),
    milesDriven: document.getElementById('miles-driven'),
    gallonsUsed: document.getElementById('gallons-used'),
    fuelCost: document.getElementById('fuel-cost'),
    wearTear: document.getElementById('wear-tear'),
    totalExpenses: document.getElementById('total-expenses'),
    expenseDelta: document.getElementById('expense-delta'),
    netProfit: document.getElementById('net-profit'),
    profitDelta: document.getElementById('profit-delta'),
    healthMessage: document.getElementById('health-message'),
    progressBar: document.getElementById('progress-bar'),
    progressText: document.getElementById('progress-text'),
    progressSection: document.getElementById('progress-section'),
    successMessage: document.getElementById('success-message'),
    odoWarning: document.getElementById('odo-warning')
};

// Función para calcular todos los valores
function calculate() {
    // Obtener valores de entrada
    const mpg = parseFloat(inputs.mpg.value) || 0;
    const gasPrice = parseFloat(inputs.gasPrice.value) || 0;
    const metaNetaObjetivo = parseFloat(inputs.metaNeta.value) || 0;
    const uberEarnings = parseFloat(inputs.uberEarnings.value) || 0;
    const lyftEarnings = parseFloat(inputs.lyftEarnings.value) || 0;
    const cashTips = parseFloat(inputs.cashTips.value) || 0;
    const odoStart = parseInt(inputs.odoStart.value) || 0;
    const odoEnd = parseInt(inputs.odoEnd.value) || 0;
    const foodCost = parseFloat(inputs.foodCost.value) || 0;
    const miscCost = parseFloat(inputs.miscCost.value) || 0;

    // Calcular ingresos brutos
    const totalGross = uberEarnings + lyftEarnings + cashTips;
    outputs.totalGross.textContent = `$${totalGross.toFixed(2)}`;

    // Calcular millas recorridas
    let milesDriven = 0.0;
    if (odoEnd > odoStart && odoStart > 0) {
        milesDriven = odoEnd - odoStart;
        outputs.odoWarning.classList.add('hidden');
    } else if (odoEnd > 0 && odoStart == 0) {
        outputs.odoWarning.classList.remove('hidden');
    } else {
        outputs.odoWarning.classList.add('hidden');
    }

    // Calcular costo de combustible
    const gallonsUsed = mpg > 0 ? milesDriven / mpg : 0;
    const fuelCost = gallonsUsed * gasPrice;

    outputs.milesDriven.textContent = `${milesDriven.toFixed(1)} mi`;
    outputs.gallonsUsed.textContent = `${gallonsUsed.toFixed(2)} gal`;
    outputs.fuelCost.textContent = `$${fuelCost.toFixed(2)}`;

    // Calcular reserva por desgaste
    const wearAndTear = milesDriven * 0.10;
    outputs.wearTear.textContent = `Reserva estimada por desgaste ($0.10/milla): $${wearAndTear.toFixed(2)} (No se descuenta del efectivo hoy, pero tenlo en cuenta)`;

    // Calcular gastos adicionales
    const additionalExpensesTotal = additionalExpenses.reduce((sum, exp) => sum + exp.amount, 0);
    
    // Calcular gastos totales y ganancia neta
    const totalExpenses = fuelCost + foodCost + miscCost + additionalExpensesTotal;
    const netProfit = totalGross - totalExpenses;

    outputs.totalExpenses.textContent = `$${totalExpenses.toFixed(2)}`;
    outputs.netProfit.textContent = `$${netProfit.toFixed(2)}`;

    // Calcular ratio de gastos
    let expenseRatio = 0.0;
    if (totalGross > 0) {
        expenseRatio = (totalExpenses / totalGross) * 100;
    }

    outputs.expenseDelta.textContent = `-${expenseRatio.toFixed(1)}% del ingreso`;
    
    const profitDelta = netProfit - metaNetaObjetivo;
    outputs.profitDelta.textContent = `$${profitDelta.toFixed(2)} vs Meta`;

    // Mostrar mensaje de salud financiera
    let healthColor = 'green';
    let healthMsg = '✅ SALUDABLE: Tus gastos están bajo control.';

    if (totalGross == 0) {
        healthMsg = 'Esperando ingresos...';
        healthColor = 'gray';
        outputs.healthMessage.classList.add('hidden');
    } else if (expenseRatio < 20) {
        healthColor = 'green';
        healthMsg = `✅ EXCELENTE: Gastos operativos al ${expenseRatio.toFixed(1)}% (Muy Rentable)`;
        outputs.healthMessage.className = 'health-message success';
        outputs.healthMessage.classList.remove('hidden');
    } else if (expenseRatio >= 20 && expenseRatio <= 35) {
        healthColor = 'orange';
        healthMsg = `⚠️ ATENCIÓN: Gastos operativos al ${expenseRatio.toFixed(1)}% (Vigila el consumo)`;
        outputs.healthMessage.className = 'health-message warning';
        outputs.healthMessage.classList.remove('hidden');
    } else {
        healthColor = 'red';
        healthMsg = `🛑 ALERTA: Gastos operativos al ${expenseRatio.toFixed(1)}% (Estás gastando demasiado)`;
        outputs.healthMessage.className = 'health-message error';
        outputs.healthMessage.classList.remove('hidden');
    }

    outputs.healthMessage.textContent = healthMsg;

    // Barra de progreso hacia la meta
    if (metaNetaObjetivo > 0) {
        let progress = Math.min(netProfit / metaNetaObjetivo, 1.0);
        if (progress < 0) progress = 0;
        
        outputs.progressBar.style.width = `${progress * 100}%`;
        outputs.progressText.textContent = `Progreso hacia la meta de $${metaNetaObjetivo} Netos: ${(progress * 100).toFixed(1)}%`;
        outputs.progressSection.classList.remove('hidden');
    } else {
        outputs.progressSection.classList.add('hidden');
    }

    // Mensaje de éxito si alcanzó la meta
    if (netProfit >= metaNetaObjetivo && metaNetaObjetivo > 0) {
        outputs.successMessage.classList.remove('hidden');
        // Animación de globos (simulada con CSS)
        createBalloons();
    } else {
        outputs.successMessage.classList.add('hidden');
    }
}

// Función para crear animación de globos
function createBalloons() {
    // Crear elementos de globos flotantes
    for (let i = 0; i < 20; i++) {
        const balloon = document.createElement('div');
        balloon.style.position = 'fixed';
        balloon.style.left = Math.random() * 100 + '%';
        balloon.style.bottom = '-50px';
        balloon.style.width = '30px';
        balloon.style.height = '40px';
        balloon.style.background = `hsl(${Math.random() * 360}, 70%, 60%)`;
        balloon.style.borderRadius = '50% 50% 50% 50% / 60% 60% 40% 40%';
        balloon.style.animation = `balloons ${2 + Math.random() * 2}s ease-out forwards`;
        balloon.style.zIndex = '9999';
        balloon.style.pointerEvents = 'none';
        document.body.appendChild(balloon);
        
        setTimeout(() => {
            balloon.remove();
        }, 4000);
    }
}

// Agregar animación de globos al CSS dinámicamente
const style = document.createElement('style');
style.textContent = `
    @keyframes balloons {
        to {
            transform: translateY(-100vh) rotate(360deg);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Agregar event listeners a todos los inputs
Object.values(inputs).forEach(input => {
    input.addEventListener('input', calculate);
    input.addEventListener('change', calculate);
});

// ========== BASE DE DATOS (IndexedDB) ==========
let db = null;

function initDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('DriverFinancesDB', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            db = request.result;
            resolve(db);
        };
        
        request.onupgradeneeded = (event) => {
            const database = event.target.result;
            
            // Crear object store para registros diarios
            if (!database.objectStoreNames.contains('dailyRecords')) {
                const objectStore = database.createObjectStore('dailyRecords', { keyPath: 'date' });
                objectStore.createIndex('date', 'date', { unique: true });
            }
            
            // Crear object store para configuración
            if (!database.objectStoreNames.contains('vehicleConfig')) {
                database.createObjectStore('vehicleConfig', { keyPath: 'id' });
            }
        };
    });
}

async function saveRecord() {
    if (!db) await initDB();
    
    const today = new Date().toISOString().split('T')[0];
    const mpg = parseFloat(inputs.mpg.value) || 0;
    const gasPrice = parseFloat(inputs.gasPrice.value) || 0;
    const metaNetaObjetivo = parseFloat(inputs.metaNeta.value) || 0;
    const uberEarnings = parseFloat(inputs.uberEarnings.value) || 0;
    const lyftEarnings = parseFloat(inputs.lyftEarnings.value) || 0;
    const cashTips = parseFloat(inputs.cashTips.value) || 0;
    const odoStart = parseInt(inputs.odoStart.value) || 0;
    const odoEnd = parseInt(inputs.odoEnd.value) || 0;
    const foodCost = parseFloat(inputs.foodCost.value) || 0;
    const miscCost = parseFloat(inputs.miscCost.value) || 0;
    
    const milesDriven = (odoEnd > odoStart && odoStart > 0) ? odoEnd - odoStart : 0;
    const gallonsUsed = mpg > 0 ? milesDriven / mpg : 0;
    const fuelCost = gallonsUsed * gasPrice;
    const totalGross = uberEarnings + lyftEarnings + cashTips;
    const wearAndTear = milesDriven * 0.10;
    const additionalExpensesTotal = additionalExpenses.reduce((sum, exp) => sum + exp.amount, 0);
    const totalExpenses = fuelCost + foodCost + miscCost + additionalExpensesTotal;
    const netProfit = totalGross - totalExpenses;
    const expenseRatio = totalGross > 0 ? (totalExpenses / totalGross) * 100 : 0;
    
    const record = {
        date: today,
        mpg, gasPrice, metaNetaObjetivo,
        uberEarnings, lyftEarnings, cashTips,
        odoStart, odoEnd, milesDriven,
        gallonsUsed, fuelCost, foodCost,
        miscCost, additionalExpenses, wearAndTear, totalGross,
        totalExpenses, netProfit, expenseRatio,
        createdAt: new Date().toISOString()
    };
    
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['dailyRecords'], 'readwrite');
        const objectStore = transaction.objectStore('dailyRecords');
        const request = objectStore.put(record);
        
        request.onsuccess = () => resolve(true);
        request.onerror = () => reject(request.error);
    });
}

async function loadTodayRecord() {
    if (!db) await initDB();
    
    const today = new Date().toISOString().split('T')[0];
    
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['dailyRecords'], 'readonly');
        const objectStore = transaction.objectStore('dailyRecords');
        const request = objectStore.get(today);
        
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function getAllRecords() {
    if (!db) await initDB();
    
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['dailyRecords'], 'readonly');
        const objectStore = transaction.objectStore('dailyRecords');
        const request = objectStore.getAll();
        
        request.onsuccess = () => {
            const records = request.result.sort((a, b) => new Date(b.date) - new Date(a.date));
            resolve(records.slice(0, 30));
        };
        request.onerror = () => reject(request.error);
    });
}

async function getStatistics() {
    const records = await getAllRecords();
    
    if (records.length === 0) {
        return {
            totalDays: 0,
            totalIncome: 0,
            totalExpenses: 0,
            totalProfit: 0,
            avgDailyProfit: 0,
            totalMiles: 0,
            totalFuelCost: 0
        };
    }
    
    const stats = records.reduce((acc, record) => {
        acc.totalIncome += record.totalGross || 0;
        acc.totalExpenses += record.totalExpenses || 0;
        acc.totalProfit += record.netProfit || 0;
        acc.totalMiles += record.milesDriven || 0;
        acc.totalFuelCost += record.fuelCost || 0;
        return acc;
    }, {
        totalDays: records.length,
        totalIncome: 0,
        totalExpenses: 0,
        totalProfit: 0,
        totalMiles: 0,
        totalFuelCost: 0
    });
    
    stats.avgDailyProfit = stats.totalProfit / stats.totalDays;
    return stats;
}

async function deleteRecord(date) {
    if (!db) await initDB();
    
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['dailyRecords'], 'readwrite');
        const objectStore = transaction.objectStore('dailyRecords');
        const request = objectStore.delete(date);
        
        request.onsuccess = () => resolve(true);
        request.onerror = () => reject(request.error);
    });
}

// Función para mostrar estadísticas
async function displayStatistics() {
    const stats = await getStatistics();
    const container = document.getElementById('statistics-container');
    
    if (stats.totalDays === 0) {
        container.innerHTML = '<p class="info-message">No hay registros aún. Guarda tu primer registro para ver estadísticas.</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Días Registrados</div>
                <div class="stat-value">${stats.totalDays}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Ingreso Total</div>
                <div class="stat-value">$${stats.totalIncome.toFixed(2)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Gastos Total</div>
                <div class="stat-value">$${stats.totalExpenses.toFixed(2)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Ganancia Total</div>
                <div class="stat-value">$${stats.totalProfit.toFixed(2)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Ganancia Promedio/Día</div>
                <div class="stat-value">$${stats.avgDailyProfit.toFixed(2)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Millas Totales</div>
                <div class="stat-value">${stats.totalMiles.toFixed(1)} mi</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Combustible Total</div>
                <div class="stat-value">$${stats.totalFuelCost.toFixed(2)}</div>
            </div>
        </div>
    `;
}

// Función para mostrar historial
async function displayHistory() {
    const records = await getAllRecords();
    const container = document.getElementById('history-container');
    
    if (records.length === 0) {
        container.innerHTML = '<p class="info-message">No hay registros en el historial.</p>';
        return;
    }
    
    container.innerHTML = '<h3>Últimos 30 Registros</h3>';
    
    records.forEach(record => {
        const recordDiv = document.createElement('div');
        recordDiv.className = 'history-item';
        recordDiv.innerHTML = `
            <div class="history-header">
                <span class="history-date">📅 ${record.date}</span>
                <span class="history-profit">Ganancia Neta: $${record.netProfit.toFixed(2)}</span>
                <button class="delete-btn" onclick="deleteRecordAndRefresh('${record.date}')">🗑️ Eliminar</button>
            </div>
            <div class="history-details">
                <div>Ingreso Bruto: $${record.totalGross.toFixed(2)}</div>
                <div>Gastos: $${record.totalExpenses.toFixed(2)}</div>
                <div>Millas: ${record.milesDriven.toFixed(1)} mi</div>
                <div>Combustible: $${record.fuelCost.toFixed(2)}</div>
            </div>
        `;
        container.appendChild(recordDiv);
    });
}

window.deleteRecordAndRefresh = async function(date) {
    if (confirm('¿Estás seguro de eliminar este registro?')) {
        await deleteRecord(date);
        await displayHistory();
        await displayStatistics();
    }
}

// Función para cambiar tabs
window.showTab = function(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(`${tabName}-tab`).classList.remove('hidden');
    event.target.classList.add('active');
    
    if (tabName === 'stats') {
        displayStatistics();
    } else if (tabName === 'history') {
        displayHistory();
    }
}

// Botón guardar
document.getElementById('save-button').addEventListener('click', async () => {
    const saveButton = document.getElementById('save-button');
    const saveMessage = document.getElementById('save-message');
    
    saveButton.disabled = true;
    saveButton.textContent = 'Guardando...';
    
    try {
        await saveRecord();
        saveMessage.textContent = '✅ Registro guardado exitosamente!';
        saveMessage.className = 'save-message success';
        saveMessage.classList.remove('hidden');
        
        // Recargar historial y estadísticas
        await displayStatistics();
        await displayHistory();
        
        setTimeout(() => {
            saveMessage.classList.add('hidden');
        }, 3000);
    } catch (error) {
        saveMessage.textContent = '❌ Error al guardar el registro';
        saveMessage.className = 'save-message error';
        saveMessage.classList.remove('hidden');
        console.error('Error:', error);
    } finally {
        saveButton.disabled = false;
        saveButton.textContent = '💾 Guardar Registro de Hoy';
    }
});

// Cargar registro de hoy al iniciar
async function loadTodayData() {
    try {
        const todayRecord = await loadTodayRecord();
        if (todayRecord) {
            inputs.mpg.value = todayRecord.mpg || 35.0;
            inputs.gasPrice.value = todayRecord.gasPrice || 3.10;
            inputs.metaNeta.value = todayRecord.metaNetaObjetivo || 200.0;
            inputs.uberEarnings.value = todayRecord.uberEarnings || 0;
            inputs.lyftEarnings.value = todayRecord.lyftEarnings || 0;
            inputs.cashTips.value = todayRecord.cashTips || 0;
            inputs.odoStart.value = todayRecord.odoStart || 0;
            inputs.odoEnd.value = todayRecord.odoEnd || 0;
            inputs.foodCost.value = todayRecord.foodCost || 0;
            inputs.miscCost.value = todayRecord.miscCost || 0;
            
            // Cargar gastos adicionales
            if (todayRecord.additionalExpenses && Array.isArray(todayRecord.additionalExpenses)) {
                additionalExpenses = todayRecord.additionalExpenses;
            } else {
                additionalExpenses = [];
            }
            
            renderAdditionalExpenses();
            calculate();
        }
    } catch (error) {
        console.error('Error cargando datos:', error);
    }
}

// Inicializar base de datos y cargar datos
initDB().then(() => {
    loadTodayData();
    displayStatistics();
}).catch(error => {
    console.error('Error inicializando base de datos:', error);
});

// Función para renderizar la lista de gastos adicionales
function renderAdditionalExpenses() {
    const container = document.getElementById('additional-expenses-list');
    const totalContainer = document.getElementById('additional-expenses-total');
    const total = additionalExpenses.reduce((sum, exp) => sum + exp.amount, 0);
    
    if (additionalExpenses.length === 0) {
        container.innerHTML = '';
        totalContainer.classList.add('hidden');
        return;
    }
    
    container.innerHTML = '<div class="expenses-list-header"><strong>Gastos agregados:</strong></div>';
    additionalExpenses.forEach((expense, idx) => {
        const expenseDiv = document.createElement('div');
        expenseDiv.className = 'expense-item';
        expenseDiv.innerHTML = `
            <span class="expense-name">📝 ${expense.name}</span>
            <span class="expense-amount">$${expense.amount.toFixed(2)}</span>
            <button class="delete-expense-btn" onclick="removeAdditionalExpense(${idx})">🗑️</button>
        `;
        container.appendChild(expenseDiv);
    });
    
    if (total > 0) {
        totalContainer.textContent = `💰 Total de gastos adicionales: $${total.toFixed(2)}`;
        totalContainer.classList.remove('hidden');
    } else {
        totalContainer.classList.add('hidden');
    }
}

// Función para agregar gasto adicional
function addAdditionalExpense() {
    const nameInput = document.getElementById('new-expense-name');
    const amountInput = document.getElementById('new-expense-amount');
    
    const name = nameInput.value.trim();
    const amount = parseFloat(amountInput.value) || 0;
    
    if (!name) {
        alert('⚠️ Ingresa una descripción para el gasto');
        return;
    }
    
    if (amount <= 0) {
        alert('⚠️ Ingresa una cantidad mayor a 0');
        return;
    }
    
    additionalExpenses.push({
        name: name,
        amount: amount
    });
    
    nameInput.value = '';
    amountInput.value = '0';
    
    renderAdditionalExpenses();
    calculate();
}

// Función para eliminar gasto adicional
window.removeAdditionalExpense = function(idx) {
    additionalExpenses.splice(idx, 1);
    renderAdditionalExpenses();
    calculate();
}

// Event listener para el botón de agregar gasto
document.getElementById('add-expense-btn').addEventListener('click', addAdditionalExpense);

// Permitir agregar con Enter
document.getElementById('new-expense-amount').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        addAdditionalExpense();
    }
});

document.getElementById('new-expense-name').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        addAdditionalExpense();
    }
});

// Calcular valores iniciales
calculate();
renderAdditionalExpenses();

