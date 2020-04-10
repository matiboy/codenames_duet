import axios from 'axios'
import {IAuthTokens,
  TokenRefreshRequest,
  useAuthTokenInterceptor} from 'axios-jwt'

const apiClient = axios.create({
  responseType: 'json',
  headers: {
    'Content-Type': 'application/json'
  }
});

const refreshEndpoint = '/auth/refresh'

const requestRefresh: TokenRefreshRequest = async (
  refreshToken: string
): Promise<string> => {
  // perform refresh
  return (await axios.post<IAuthTokens>(refreshEndpoint, { token: refreshToken })).data
    .accessToken;
};

// add interceptor to axios instance
useAuthTokenInterceptor(apiClient, { requestRefresh });

export const login = async (token: string): Promise<IAuthTokens> => {
  const response = await apiClient.post<IAuthTokens>('/login', {token})
  return response.data
}
