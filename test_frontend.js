import axios from 'axios';

async function test() {
  try {
    const res = await axios.get('http://localhost:8000/api/vehicles/520475f0-2f8c-48ee-8d59-9e40650cb33b');
    console.log("Success:", res.status);
  } catch (err) {
    console.error("Error:", err.message);
    if (err.response) {
      console.error("Status:", err.response.status);
      console.error("Data:", err.response.data);
    }
  }
}

test();
