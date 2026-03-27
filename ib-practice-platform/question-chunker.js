/**
 * Question chunking utility
 * Splits a large questions.json into smaller subject-specific files
 * Run this in Node.js or in the browser to pre-split your data
 * 
 * Usage (Node.js):
 * node question-chunker.js questions.json
 * 
 * This creates subject-specific files like:
 * - questions-math_ai.json
 * - questions-math_aa.json
 * - etc.
 */

const fs = require('fs');
const path = require('path');

function chunkQuestions(inputFile) {
  console.log(`Reading ${inputFile}...`);
  
  // Read the input file
  let questions = [];
  try {
    const data = fs.readFileSync(inputFile, 'utf-8');
    const parsed = JSON.parse(data);
    questions = Array.isArray(parsed) ? parsed : (parsed.questions || []);
  } catch (e) {
    console.error(`Failed to read ${inputFile}:`, e.message);
    process.exit(1);
  }

  console.log(`Loaded ${questions.length} total questions`);

  // Group by subject
  const chunks = {};
  for (const q of questions) {
    const subject = q.subject || 'unknown';
    if (!chunks[subject]) {
      chunks[subject] = [];
    }
    chunks[subject].push(q);
  }

  // Write subject-specific files
  const outputDir = path.dirname(inputFile);
  let totalWritten = 0;

  for (const [subject, qs] of Object.entries(chunks)) {
    const filename = path.join(outputDir, `questions-${subject}.json`);
    try {
      fs.writeFileSync(filename, JSON.stringify(qs, null, 2), 'utf-8');
      console.log(`✓ Wrote ${qs.length} questions to ${path.basename(filename)}`);
      totalWritten += qs.length;
    } catch (e) {
      console.error(`Failed to write ${filename}:`, e.message);
    }
  }

  console.log(`\nChunking complete: ${totalWritten}/${questions.length} questions saved`);
  console.log(`Created ${Object.keys(chunks).length} subject-specific files`);
}

// Run if called directly
if (require.main === module) {
  const inputFile = process.argv[2] || 'questions.json';
  chunkQuestions(inputFile);
}

module.exports = { chunkQuestions };
