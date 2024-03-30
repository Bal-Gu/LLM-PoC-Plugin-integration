import { createContext, Dispatch, SetStateAction } from 'react';

type AuthTokenContextType = [string | null, Dispatch<SetStateAction<string | null>> | null];

export const AuthTokenContext = createContext<AuthTokenContextType>([null, null]);