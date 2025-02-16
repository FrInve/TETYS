// src/app/services/api.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpParams  } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})

export class ApiService {
  private baseUrl = 'https://geco.deib.polimi.it/tetys_api';  // Replace with your backend URL

  constructor(private http: HttpClient) {}

  // Example method to get data from an endpoint
  getData(endpoint: string, paramsObj?: any): Observable<any> {
    const url = `${this.baseUrl}/${endpoint}`;
    let params = new HttpParams();

    // If there are parameters, append them to HttpParams
    if (paramsObj) {
      Object.keys(paramsObj).forEach((key) => {
        params = params.append(key, paramsObj[key]);
      });
    }
    
    return this.http.get(url, { params }).pipe(
      catchError(this.handleError)
    );
  }

  // Example method to post data to an endpoint
  postData(endpoint: string, body: any, paramsObj?: any): Observable<any> {
    const url = `${this.baseUrl}/${endpoint}`;
    let params = new HttpParams();

    // If there are parameters, append them to HttpParams
    if (paramsObj) {
      Object.keys(paramsObj).forEach((key) => {
        params = params.append(key, paramsObj[key]);
      });
    }
    
    return this.http.post(url, body, { params }).pipe(
      catchError(this.handleError)
    );
  }

  // Handle errors from the backend
  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {
      // Client-side or network error
      console.error('An error occurred:', error.error.message);
    } else {
      // Backend returned an unsuccessful response code
      console.error(
        `Backend returned code ${error.status}, ` +
        `body was: ${error.error}`);
    }
    // Return an observable with a user-facing error message
    return throwError(
      'Something went wrong; please try again later.');
  }
}
