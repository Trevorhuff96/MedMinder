import { createHash } from 'crypto';
import { execFileSync } from 'child_process';
import { Page, expect } from '@playwright/test';

const DB_PATH = 'medminder.db';
const TEST_EMAIL_PATTERN = 'pw_%@example.com';
const TEST_NAME_PATTERN = 'Playwright %';

type UserRole = 'Patient' | 'Doctor';

type UserSeed = {
  email: string;
  password: string;
  name: string;
  role: UserRole;
  speciality?: string;
  officeHours?: string;
  offDay?: string;
};

type AppointmentSeed = {
  patientEmail: string;
  doctorEmail: string;
  date: string;
  time: string;
  status?: 'confirmed' | 'cancelled';
  notes?: string;
};

type PrescriptionSeed = {
  patientEmail: string;
  patientName: string;
  doctorEmail: string;
  diagnosis: string;
  followUpDays: number;
  generalNotes: string;
  medicines: Array<{
    name: string;
    dosage: string;
    frequency: string;
    days: number;
    route: string;
    timing: string;
    directions: string;
  }>;
};

function sqlEscape(value: string): string {
  return value.replace(/'/g, "''");
}

function runSql(sql: string): string {
  return execFileSync('sqlite3', [DB_PATH, sql], { encoding: 'utf8' }).trim();
}

function hashPassword(password: string): string {
  return createHash('sha256').update(password).digest('hex');
}

export function uniqueId(label: string): string {
  return `${label}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function cleanupPlaywrightData(): void {
  runSql(`
    PRAGMA foreign_keys = OFF;
    DELETE FROM appointment_note_syntheses
      WHERE appointment_id IN (
        SELECT appointment_id
        FROM appointments
        WHERE patient_email LIKE '${TEST_EMAIL_PATTERN}'
           OR doctor_email LIKE '${TEST_EMAIL_PATTERN}'
      );
    DELETE FROM appointments
      WHERE patient_email LIKE '${TEST_EMAIL_PATTERN}'
         OR doctor_email LIKE '${TEST_EMAIL_PATTERN}';
    DELETE FROM care_team
      WHERE patient_email LIKE '${TEST_EMAIL_PATTERN}'
         OR doctor_email LIKE '${TEST_EMAIL_PATTERN}';
    DELETE FROM prescription
      WHERE doctor_email LIKE '${TEST_EMAIL_PATTERN}'
         OR patient_name LIKE '${TEST_NAME_PATTERN}';
    DELETE FROM doctors WHERE email LIKE '${TEST_EMAIL_PATTERN}';
    DELETE FROM patients WHERE email LIKE '${TEST_EMAIL_PATTERN}';
    DELETE FROM users WHERE email LIKE '${TEST_EMAIL_PATTERN}';
    PRAGMA foreign_keys = ON;
  `);
}

export function seedUser(user: UserSeed): void {
  const createdAt = new Date().toISOString();
  const passwordHash = hashPassword(user.password);
  const email = sqlEscape(user.email);
  const name = sqlEscape(user.name);
  const role = sqlEscape(user.role);

  runSql(`
    INSERT INTO users (email, name, password, role, created_at)
    VALUES ('${email}', '${name}', '${passwordHash}', '${role}', '${createdAt}');
  `);

  if (user.role === 'Doctor') {
    runSql(`
      INSERT INTO doctors (email, dob, gender, phone, address, speciality, office_hours, off_day)
      VALUES (
        '${email}',
        '1984-07-16',
        'Female',
        '5551112222',
        '1 Playwright Clinic, New York, New York 10001, United States',
        '${sqlEscape(user.speciality ?? 'General Practitioner')}',
        '${sqlEscape(user.officeHours ?? '9:00 AM to 6:00 PM')}',
        '${sqlEscape(user.offDay ?? 'Friday')}'
      );
    `);
  } else {
    runSql(`
      INSERT INTO patients (email, dob, gender, phone, address)
      VALUES (
        '${email}',
        '1995-01-15',
        'Male',
        '5552223333',
        '1 Playwright Lane, Charlotte, North Carolina 28223, United States'
      );
    `);
  }
}

export function seedCareTeam(patientEmail: string, doctorEmail: string): void {
  const linkedAt = new Date().toISOString();
  runSql(`
    INSERT OR IGNORE INTO care_team (patient_email, doctor_email, linked_at)
    VALUES ('${sqlEscape(patientEmail)}', '${sqlEscape(doctorEmail)}', '${linkedAt}');
  `);
}

export function seedAppointment(appointment: AppointmentSeed): number {
  const createdAt = new Date().toISOString();
  runSql(`
    INSERT INTO appointments (
      patient_email,
      doctor_email,
      appointment_date,
      appointment_time,
      status,
      notes,
      created_at
    )
    VALUES (
      '${sqlEscape(appointment.patientEmail)}',
      '${sqlEscape(appointment.doctorEmail)}',
      '${sqlEscape(appointment.date)}',
      '${sqlEscape(appointment.time)}',
      '${sqlEscape(appointment.status ?? 'confirmed')}',
      '${sqlEscape(appointment.notes ?? '')}',
      '${createdAt}'
    );
  `);
  seedCareTeam(appointment.patientEmail, appointment.doctorEmail);
  return Number(runSql(`
    SELECT appointment_id
    FROM appointments
    WHERE patient_email = '${sqlEscape(appointment.patientEmail)}'
      AND doctor_email = '${sqlEscape(appointment.doctorEmail)}'
      AND appointment_date = '${sqlEscape(appointment.date)}'
      AND appointment_time = '${sqlEscape(appointment.time)}'
    ORDER BY appointment_id DESC
    LIMIT 1;
  `));
}

export function seedPrescription(prescription: PrescriptionSeed): void {
  const createdAt = new Date().toISOString();
  const patientId = runSql(`
    SELECT patient_id
    FROM patients
    WHERE email = '${sqlEscape(prescription.patientEmail)}'
    LIMIT 1;
  `);
  const medicinesJson = sqlEscape(JSON.stringify(prescription.medicines));

  runSql(`
    INSERT INTO prescription (
      patient_id,
      patient_name,
      doctor_email,
      diagnosis,
      follow_up_days,
      general_notes,
      medicines_json,
      created_at
    )
    VALUES (
      ${patientId || 'NULL'},
      '${sqlEscape(prescription.patientName)}',
      '${sqlEscape(prescription.doctorEmail)}',
      '${sqlEscape(prescription.diagnosis)}',
      ${prescription.followUpDays},
      '${sqlEscape(prescription.generalNotes)}',
      '${medicinesJson}',
      '${createdAt}'
    );
  `);
  seedCareTeam(prescription.patientEmail, prescription.doctorEmail);
}

export async function logOut(page: Page): Promise<void> {
  await page.goto('/?logout=1');
  await expect(page.getByText('Smarter Health Management Starts Here.')).toBeVisible();
}

export async function login(page: Page, email: string, password: string, name: string, role: UserRole): Promise<void> {
  await logOut(page);
  await page.getByRole('button', { name: 'Sign In' }).click();
  await expect(page.getByText('Sign In to Your Account')).toBeVisible();
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'Password' }).fill(password);
  await page.getByRole('button', { name: 'Sign In' }).click();
  await expect(page.getByText(`Welcome back, ${name}!`).or(page.getByText(`Welcome back, Dr. ${name}!`))).toBeVisible();
  await expect(page.getByText(`Account: ${email}`)).toBeVisible();
  await expect(page.getByText(`Role: ${role}`)).toBeVisible();
}

export async function openMenu(page: Page): Promise<void> {
  await page.getByRole('button', { name: '☰' }).click();
}
