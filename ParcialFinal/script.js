// Conexión con API del modelo real
// Detecta automáticamente si está en desarrollo local o en producción
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/predict'
    : '/predict';

document.getElementById('creditForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Deshabilitar botón mientras procesa
    const button = document.querySelector('.btn-predict');
    const originalText = button.textContent;
    button.textContent = '⏳ Calculando...';
    button.disabled = true;
    
    // Obtener valores del formulario
    const data = {
        utilization: parseFloat(document.getElementById('utilization').value),
        age: parseInt(document.getElementById('age').value),
        late30: parseInt(document.getElementById('late30').value),
        debtRatio: parseFloat(document.getElementById('debtRatio').value),
        income: parseFloat(document.getElementById('income').value),
        openLines: parseInt(document.getElementById('openLines').value),
        late90: parseInt(document.getElementById('late90').value),
        realEstate: parseInt(document.getElementById('realEstate').value),
        late60: parseInt(document.getElementById('late60').value),
        dependents: parseInt(document.getElementById('dependents').value)
    };
    
    try {
        // Llamar a la API con el modelo real
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Mostrar resultados con predicción real
            displayResults(result.probability);
        } else {
            throw new Error(result.error || 'Error en la predicción');
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('⚠️ No se pudo conectar con el servidor. Asegúrate de que la API esté corriendo (python api.py)');
    } finally {
        // Restaurar botón
        button.textContent = originalText;
        button.disabled = false;
    }
});



function displayResults(probability) {
    // Mostrar sección de resultados
    const resultCard = document.getElementById('result');
    resultCard.classList.remove('hidden');
    
    // Scroll suave hacia resultados
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Actualizar probabilidad
    const probPercent = (probability * 100).toFixed(2);
    document.getElementById('probability').textContent = probPercent + '%';
    
    // Actualizar barra de progreso
    const progressFill = document.getElementById('progressFill');
    progressFill.style.width = probPercent + '%';
    
    // Determinar nivel de riesgo
    let riskLevel, riskClass, recommendation;
    
    if (probability < 0.3) {
        riskLevel = '✅ Riesgo Bajo';
        riskClass = 'risk-low';
        recommendation = '<strong>Recomendación:</strong> Cliente de bajo riesgo. Se puede aprobar el crédito con condiciones estándar. El perfil crediticio es favorable y la probabilidad de morosidad es baja.';
    } else if (probability < 0.6) {
        riskLevel = '⚠️ Riesgo Medio';
        riskClass = 'risk-medium';
        recommendation = '<strong>Recomendación:</strong> Cliente de riesgo moderado. Se sugiere análisis adicional antes de aprobar. Considerar requisitos adicionales como garantías o co-deudor. Monitoreo cercano recomendado.';
    } else {
        riskLevel = '🚨 Riesgo Alto';
        riskClass = 'risk-high';
        recommendation = '<strong>Recomendación:</strong> Cliente de alto riesgo. No se recomienda aprobar el crédito sin medidas de mitigación significativas. Si se aprueba, considerar monto reducido, tasas ajustadas al riesgo, y garantías sólidas.';
    }
    
    // Actualizar badge de riesgo
    const riskBadge = document.getElementById('riskLevel');
    riskBadge.textContent = riskLevel;
    riskBadge.className = 'risk-badge ' + riskClass;
    
    // Actualizar recomendación
    document.getElementById('recommendation').innerHTML = recommendation;
}

// Validación en tiempo real
document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('input', function() {
        if (this.value !== '') {
            const value = parseFloat(this.value);
            const min = parseFloat(this.min);
            const max = parseFloat(this.max);
            
            if (value < min) this.value = min;
            if (value > max) this.value = max;
        }
    });
});
