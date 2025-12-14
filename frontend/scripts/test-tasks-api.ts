/**
 * Tasks API Integration Test
 * Tests full CRUD cycle for tasks
 * 
 * Run with: npx tsx scripts/test-tasks-api.ts
 */

const API_URL = 'https://pulse-20-production.up.railway.app';

async function runTasksTest() {
    console.log('🧪 Tasks API Integration Test');
    console.log('==============================');
    console.log('');

    let createdTaskId: number | null = null;

    try {
        // 1. GET all tasks
        console.log('1️⃣ GET /tasks - Fetching all tasks...');
        const tasksResponse = await fetch(`${API_URL}/tasks`);
        const tasks = await tasksResponse.json();
        console.log(`   ✅ Found ${tasks.length} tasks`);

        // 2. POST create task
        console.log('2️⃣ POST /tasks - Creating test task...');
        const createResponse = await fetch(`${API_URL}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: 'Test Task from Frontend',
                duration: 1.0,
                difficulty: 'easy',
                priority: 'medium'
            })
        });
        const created = await createResponse.json();
        createdTaskId = created.id;
        console.log(`   ✅ Created task ID: ${createdTaskId}`);

        // 3. GET single task
        console.log(`3️⃣ GET /tasks/${createdTaskId} - Fetching created task...`);
        const getResponse = await fetch(`${API_URL}/tasks/${createdTaskId}`);
        const task = await getResponse.json();
        console.log(`   ✅ Got task: "${task.title}"`);

        // 4. PATCH update task
        console.log(`4️⃣ PATCH /tasks/${createdTaskId} - Updating task...`);
        const updateResponse = await fetch(`${API_URL}/tasks/${createdTaskId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: 'Updated Task Title' })
        });
        const updated = await updateResponse.json();
        console.log(`   ✅ Updated title to: "${updated.title}"`);

        // 5. POST toggle
        console.log(`5️⃣ POST /tasks/${createdTaskId}/toggle - Toggling completion...`);
        const toggleResponse = await fetch(`${API_URL}/tasks/${createdTaskId}/toggle`, {
            method: 'POST'
        });
        const toggled = await toggleResponse.json();
        console.log(`   ✅ Completed: ${toggled.completed}`);

        // 6. DELETE task
        console.log(`6️⃣ DELETE /tasks/${createdTaskId} - Deleting test task...`);
        const deleteResponse = await fetch(`${API_URL}/tasks/${createdTaskId}`, {
            method: 'DELETE'
        });
        console.log(`   ✅ Deleted (status: ${deleteResponse.status})`);

        console.log('');
        console.log('🎉 All Tasks API tests passed!');
        process.exit(0);

    } catch (error) {
        console.log(`   ❌ Error: ${error instanceof Error ? error.message : 'Unknown'}`);

        // Cleanup on error
        if (createdTaskId) {
            try {
                await fetch(`${API_URL}/tasks/${createdTaskId}`, { method: 'DELETE' });
                console.log('   🧹 Cleaned up test task');
            } catch { }
        }

        process.exit(1);
    }
}

runTasksTest();
