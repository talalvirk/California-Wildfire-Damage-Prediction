import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface PredictionResponse {
  prediction: number;
  label: string;
  probability_damage: number;
  probability_no_damage: number;
  model_version: string;
  warnings: string[];
}

@Injectable({ providedIn: 'root' })
export class PredictionService {
  private http = inject(HttpClient);

  predict(payload: Record<string, number | null>): Observable<PredictionResponse> {
    return this.http.post<PredictionResponse>('/api/predict', payload);
  }
}