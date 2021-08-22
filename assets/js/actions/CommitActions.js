import * as types from './ActionTypes';

export const createRepositorySuccess = (response, successMessage, message) => ({
  type: types.CREATE_REPOSITORY_SUCCESS,
  payload: {response, successMessage, message},
});

export const getCommitsSuccess = commits => ({
  type: types.GET_COMMITS_SUCCESS,
  payload: commits,
});
