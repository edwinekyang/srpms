import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SidenavComponent } from './sidenav.component';
import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {ContractMgtService} from '../contract-mgt.service';
import {HttpClient} from '@angular/common/http';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';

describe('SidenavComponent', () => {
  let component: SidenavComponent;
  let fixture: ComponentFixture<SidenavComponent>;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      declarations: [ SidenavComponent ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      providers: [
        ContractMgtService,
      ],
    })
    .compileComponents();

    // Inject the http service and test controller for each test
    httpClient = TestBed.get(HttpClient);
    httpTestingController = TestBed.get(HttpTestingController);

    // Inject the mock ID of srpmsUser
    localStorage.setItem('srpmsUser', JSON.stringify({id: 0}));
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SidenavComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });
/*
  it('should create', () => {
    expect(component).toBeTruthy();
  });*/
});
