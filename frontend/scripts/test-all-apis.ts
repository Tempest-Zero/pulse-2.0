/**
 * Comprehensive API Test Suite
 * Tests all API modules against Railway deployment
 * 
 * Run with: npx tsx scripts/test-all-apis.ts
 */

// Use dynamic import and direct fetch instead of the modules
// since we're running outside Next.js context

const API_URL = 'https://pulse-20-production.up.railway.app';

interface TestResult {
    module: string;
    passed: boolean;
    message: string;
}

async function testEndpoint(name: string, endpoint: string): Promise<TestResult> {
    try {
        const response = await fetch(`${API_URL}${endpoint}`);
        if (response.ok) {
            const data = await response.json();
            return { module: name, passed: true, message: `✅ ${name}: OK (${JSON.stringify(data).slice(0, 50)}...)` };
        } else {
            return { module: name, passed: false, message: `❌ ${name}: HTTP ${response.status}` };
        }
    } catch (error) {
        return { module: name, passed: false, message: `❌ ${name}: ${error instanceof Error ? error.message : 'Unknown error'}` };
    }
}

async function runTests() {
    console.log('🚀 PULSE API Integration Test Suite');
    console.log('=====================================');
    console.log(`📡 Testing against: ${API_URL}`);
    console.log('');

    const results: TestResult[] = [];

    // Test 1: Root endpoint
    console.log('Testing root endpoint...');
    results.push(await testEndpoint('Root', '/'));
    console.log(results[results.length - 1].message);

    // Test 2: Health check
    console.log('Testing health endpoint...');
    results.push(await testEndpoint('Health', '/health'));
    console.log(results[results.length - 1].message);

    // Test 3: Tasks API
    console.log('Testing Tasks API...');
    results.push(await testEndpoint('Tasks', '/tasks'));
    console.log(results[results.length - 1].message);

    // Test 4: Schedule API
    console.log('Testing Schedule API...');
    results.push(await testEndpoint('Schedule', '/schedule'));
    console.log(results[results.length - 1].message);

    // Test 5: Mood API
    console.log('Testing Mood API...');
    results.push(await testEndpoint('Mood', '/mood/current'));
    console.log(results[results.length - 1].message);

    // Test 6: Reflections API
    console.log('Testing Reflections API...');
    results.push(await testEndpoint('Reflections', '/reflections'));
    console.log(results[results.length - 1].message);

    // Summary
    console.log('');
    console.log('=====================================');
    console.log('📊 SUMMARY');
    console.log('=====================================');

    const passed = results.filter(r => r.passed).length;
    const total = results.length;

    results.forEach(r => {
        console.log(`  ${r.passed ? '✅' : '❌'} ${r.module}`);
    });

    console.log('');
    console.log(`Pass Rate: ${passed}/${total} (${Math.round(passed / total * 100)}%)`);
    console.log('');

    if (passed === total) {
        console.log('🎉 ALL SYSTEMS GO! Ready for component integration.');
        process.exit(0);
    } else {
        console.log('⚠️  Some tests failed. Check the Railway deployment.');
        process.exit(1);
    }
}

runTests();
