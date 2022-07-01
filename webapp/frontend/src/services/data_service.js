import axios from 'axios';


const dataServer = ' http://127.0.0.1:5000';

export default {
  fetchEvaluationResult: (inputJson) => axios.get(`${dataServer}/data_server/evaluation?floor_plan=${inputJson}`).then((response) => response.data),
};

