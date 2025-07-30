#!/usr/bin/env node

/**
 * Deployment script for Netlify
 * Prepares frontend files and copies alerts.json to root
 */

const fs = require('fs');
const path = require('path');

console.log('🚀 Preparing files for Netlify deployment...');

// Files to copy to root for deployment
const filesToCopy = [
    'index.html',
    'styles.css', 
    'script.js',
    'README.md'
];

// Check if backend/alerts.json exists
const alertsPath = path.join(__dirname, 'backend', 'alerts.json');
if (fs.existsSync(alertsPath)) {
    console.log('✅ Found alerts.json in backend directory');
    
    // Copy alerts.json to root
    const alertsContent = fs.readFileSync(alertsPath, 'utf8');
    fs.writeFileSync(path.join(__dirname, 'alerts.json'), alertsContent);
    console.log('✅ Copied alerts.json to root directory');
} else {
    console.log('⚠️  No alerts.json found in backend directory');
    console.log('   Make sure the backend is running and generating alerts.json');
}

// Update script.js to use root alerts.json for deployment
const scriptPath = path.join(__dirname, 'script.js');
if (fs.existsSync(scriptPath)) {
    let scriptContent = fs.readFileSync(scriptPath, 'utf8');
    
    // Replace backend/alerts.json with alerts.json for deployment
    scriptContent = scriptContent.replace(
        /'backend\/alerts\.json'/g, 
        "'alerts.json'"
    );
    
    fs.writeFileSync(scriptPath, scriptContent);
    console.log('✅ Updated script.js for deployment (alerts.json path)');
}

console.log('\n📁 Files ready for deployment:');
filesToCopy.forEach(file => {
    if (fs.existsSync(path.join(__dirname, file))) {
        console.log(`   ✅ ${file}`);
    } else {
        console.log(`   ❌ ${file} (missing)`);
    }
});

if (fs.existsSync(path.join(__dirname, 'alerts.json'))) {
    console.log('   ✅ alerts.json');
} else {
    console.log('   ❌ alerts.json (missing)');
}

console.log('\n🎯 Next steps:');
console.log('1. Upload these files to Netlify:');
console.log('   - index.html');
console.log('   - styles.css');
console.log('   - script.js');
console.log('   - alerts.json');
console.log('   - README.md (optional)');
console.log('\n2. Or use Netlify CLI:');
console.log('   netlify deploy --prod');

console.log('\n✨ Deployment preparation complete!'); 