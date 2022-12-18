import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { Device, Group } from 'src/app/model';
import { apiUrl } from 'src/environments';

@Component({
  selector: 'app-api',
  templateUrl: './api.component.html',
  styleUrls: ['./api.component.css']
})
export class ApiComponent {
  constructor(private httpClient: HttpClient) { }

  getGroups(): Observable<Group[]> {
    return this.httpClient.get<Group[]>(apiUrl + 'groups/');
  }

  getDevices(): Observable<Device[]> {
    return this.httpClient.get<Device[]>(apiUrl + 'devices/');
  }

  getGroup(id: number): Observable<Group> {
    return this.httpClient.get<Group>(apiUrl + `group/${id}`);
  }

  putGroup(id: number, upper_threshold: number) {
    const httpOptions = {
      headers: { 'Content-Type': 'application/json' },
      params: {'upper_threshold':  upper_threshold}
    };
    return this.httpClient.put(apiUrl + `group/${id}/` , null, httpOptions);
  }
}
