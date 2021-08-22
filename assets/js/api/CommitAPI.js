import axios from 'axios';
import {reset} from 'redux-form';
import store from '../store';
import {
  createRepositorySuccess, getCommitsSuccess,
} from '../actions/CommitActions';

export const getCommits = () => axios.get(`/api/commits/`)
  .then((response) => {
    store.dispatch(getCommitsSuccess({...response.data}));
  });

export const createRepository = (values, headers, formDispatch) => axios.post('/api/repositories/', values, {headers})
  .then((response) => {
    const message = `Created ${response.data.name}`;
    store.dispatch(createRepositorySuccess(response.data, true, message));
    formDispatch(reset('repoCreate'));
  }).catch((error) => {
    const err = error.response;
    const status = error.response.status;
    let message;

    if(status == 400)
      message = "Repository already exists in database";
    else if(status == 404)
      message = "Not Found in GitHub";
    else if(status.toString()[0] == 5)
      message = "We are having problems to do this action now";

    store.dispatch(createRepositorySuccess(error.response.data, false, message));
    formDispatch(reset('repoCreate'));
  });
