import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<800'],
  },
};

export default function () {
  const url = 'http://localhost:8000/api/v1/slides/build';
  const payload = JSON.stringify([
    {
      title: 'Intro',
      body: 'Welcome to the deck',
      image: null,
      notes: 'Speaker notes here',
    },
    {
      title: 'History',
      body: 'A brief history',
      image: null,
      notes: null,
    },
  ]);
  const params = {
    headers: { 'Content-Type': 'application/json' },
  };
  let res = http.post(url, payload, params);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
} 