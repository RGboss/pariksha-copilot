package com.pariksha.copilot.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pariksha.copilot.data.EXAM_OPTIONS
import com.pariksha.copilot.ui.theme.*

enum class AuthTab { SIGN_IN, SIGN_UP }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AuthScreen(
    isLoading: Boolean,
    errorMessage: String?,
    onLogin: (email: String, pass: String) -> Unit,
    onSignup: (name: String, email: String, exam: String, pass: String) -> Unit,
    onDemoLogin: () -> Unit,
    onDismissError: () -> Unit
) {
    var activeTab by remember { mutableStateOf(AuthTab.SIGN_IN) }

    // Sign In State
    var loginEmail by remember { mutableStateOf("") }
    var loginPassword by remember { mutableStateOf("") }
    var showLoginPassword by remember { mutableStateOf(false) }

    // Sign Up State
    var signupName by remember { mutableStateOf("") }
    var signupEmail by remember { mutableStateOf("") }
    var signupExam by remember { mutableStateOf("SEBI Grade A (IT Stream)") }
    var signupPassword by remember { mutableStateOf("") }
    var showSignupPassword by remember { mutableStateOf(false) }
    var showExamPicker by remember { mutableStateOf(false) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Slate950)
            .padding(16.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .widthIn(max = 480.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(20.dp)
        ) {
            // Scholarly Header
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(60.dp)
                        .clip(RoundedCornerShape(18.dp))
                        .background(Amber500.copy(alpha = 0.15f))
                        .border(1.dp, Amber500.copy(alpha = 0.4f), RoundedCornerShape(18.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        Icons.Default.School,
                        contentDescription = "Cap",
                        tint = Amber400,
                        modifier = Modifier.size(34.dp)
                    )
                }

                Text(
                    text = "Govt Exam Study Portal",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.ExtraBold,
                    color = Slate100,
                    letterSpacing = (-0.5).sp
                )

                Text(
                    text = "TARGET ALL INDIA RANK (AIR) • 24/7 FACULTY MENTORSHIP",
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.Bold,
                    color = Amber400,
                    letterSpacing = 1.sp
                )

                Text(
                    text = "Personalized Topper's Study Routines & Smart Digital Book Vault",
                    style = MaterialTheme.typography.bodySmall,
                    color = Slate400,
                    textAlign = TextAlign.Center
                )
            }

            // Card Container
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(24.dp),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                border = androidx.compose.foundation.BorderStroke(1.dp, Slate800)
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // Tab Selector: Sign In vs Sign Up
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(Slate950)
                            .border(1.dp, Slate800, RoundedCornerShape(14.dp))
                            .padding(4.dp)
                    ) {
                        Button(
                            onClick = { activeTab = AuthTab.SIGN_IN; onDismissError() },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(10.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (activeTab == AuthTab.SIGN_IN) Amber500 else Color.Transparent,
                                contentColor = if (activeTab == AuthTab.SIGN_IN) Slate950 else Slate400
                            ),
                            elevation = null
                        ) {
                            Text(
                                "Aspirant Sign In",
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp
                            )
                        }

                        Button(
                            onClick = { activeTab = AuthTab.SIGN_UP; onDismissError() },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(10.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (activeTab == AuthTab.SIGN_UP) Amber500 else Color.Transparent,
                                contentColor = if (activeTab == AuthTab.SIGN_UP) Slate950 else Slate400
                            ),
                            elevation = null
                        ) {
                            Text(
                                "Start Free Prep",
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp
                            )
                        }
                    }

                    // Error Banner
                    errorMessage?.let { err ->
                        Surface(
                            modifier = Modifier.fillMaxWidth(),
                            color = Rose500.copy(alpha = 0.15f),
                            shape = RoundedCornerShape(12.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, Rose500.copy(alpha = 0.4f))
                        ) {
                            Row(
                                modifier = Modifier.padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Icon(Icons.Default.ErrorOutline, "Error", tint = Rose500, modifier = Modifier.size(18.dp))
                                Text(
                                    text = err,
                                    color = Rose500,
                                    style = MaterialTheme.typography.bodySmall,
                                    modifier = Modifier.weight(1f)
                                )
                                IconButton(onClick = onDismissError, modifier = Modifier.size(20.dp)) {
                                    Icon(Icons.Default.Close, "Dismiss", tint = Rose500, modifier = Modifier.size(16.dp))
                                }
                            }
                        }
                    }

                    // SIGN IN VIEW
                    if (activeTab == AuthTab.SIGN_IN) {
                        Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                            OutlinedTextField(
                                value = loginEmail,
                                onValueChange = { loginEmail = it },
                                modifier = Modifier.fillMaxWidth(),
                                label = { Text("Registered Email") },
                                placeholder = { Text("aspirant@examportal.in") },
                                leadingIcon = { Icon(Icons.Default.Email, "Email", tint = Slate400) },
                                singleLine = true,
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                                shape = RoundedCornerShape(14.dp),
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Amber500,
                                    unfocusedBorderColor = Slate700,
                                    focusedContainerColor = Slate950,
                                    unfocusedContainerColor = Slate950
                                )
                            )

                            OutlinedTextField(
                                value = loginPassword,
                                onValueChange = { loginPassword = it },
                                modifier = Modifier.fillMaxWidth(),
                                label = { Text("Password") },
                                placeholder = { Text("••••••••") },
                                leadingIcon = { Icon(Icons.Default.Lock, "Lock", tint = Slate400) },
                                singleLine = true,
                                visualTransformation = if (showLoginPassword) VisualTransformation.None else PasswordVisualTransformation(),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                                trailingIcon = {
                                    IconButton(onClick = { showLoginPassword = !showLoginPassword }) {
                                        Icon(
                                            if (showLoginPassword) Icons.Default.VisibilityOff else Icons.Default.Visibility,
                                            "Toggle visibility",
                                            tint = Slate400
                                        )
                                    }
                                },
                                shape = RoundedCornerShape(14.dp),
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Amber500,
                                    unfocusedBorderColor = Slate700,
                                    focusedContainerColor = Slate950,
                                    unfocusedContainerColor = Slate950
                                )
                            )

                            Button(
                                onClick = { onLogin(loginEmail, loginPassword) },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(48.dp),
                                enabled = !isLoading,
                                shape = RoundedCornerShape(14.dp),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = Amber500,
                                    contentColor = Slate950
                                )
                            ) {
                                if (isLoading) {
                                    CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp, color = Slate950)
                                } else {
                                    Text("Enter Study Desk →", fontWeight = FontWeight.ExtraBold, fontSize = 14.sp)
                                }
                            }

                            // Quick Demo Login Button
                            OutlinedButton(
                                onClick = onDemoLogin,
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(14.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, Amber500.copy(alpha = 0.5f)),
                                colors = ButtonDefaults.outlinedButtonColors(
                                    contentColor = Amber400
                                )
                            ) {
                                Icon(Icons.Default.Bolt, contentDescription = null, modifier = Modifier.size(18.dp))
                                Spacer(Modifier.width(6.dp))
                                Text(
                                    "⚡ Quick Demo Login (Aspirant Rahul • SEBI Grade A)",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }
                    } else {
                        // SIGN UP VIEW
                        Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                            OutlinedTextField(
                                value = signupName,
                                onValueChange = { signupName = it },
                                modifier = Modifier.fillMaxWidth(),
                                label = { Text("Aspirant Name") },
                                placeholder = { Text("e.g. Vikram Sharma") },
                                leadingIcon = { Icon(Icons.Default.Person, "Name", tint = Slate400) },
                                singleLine = true,
                                shape = RoundedCornerShape(14.dp),
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Amber500,
                                    unfocusedBorderColor = Slate700,
                                    focusedContainerColor = Slate950,
                                    unfocusedContainerColor = Slate950
                                )
                            )

                            OutlinedTextField(
                                value = signupEmail,
                                onValueChange = { signupEmail = it },
                                modifier = Modifier.fillMaxWidth(),
                                label = { Text("Email Address") },
                                placeholder = { Text("vikram@portal.in") },
                                leadingIcon = { Icon(Icons.Default.Email, "Email", tint = Slate400) },
                                singleLine = true,
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                                shape = RoundedCornerShape(14.dp),
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Amber500,
                                    unfocusedBorderColor = Slate700,
                                    focusedContainerColor = Slate950,
                                    unfocusedContainerColor = Slate950
                                )
                            )

                            // Target Exam Selector Card
                            OutlinedCard(
                                onClick = { showExamPicker = true },
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(14.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, Slate700),
                                colors = CardDefaults.outlinedCardColors(containerColor = Slate950)
                            ) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(14.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Icon(Icons.Default.Flag, "Target", tint = Amber400, modifier = Modifier.size(20.dp))
                                        Spacer(Modifier.width(10.dp))
                                        Column {
                                            Text("Target Examination", style = MaterialTheme.typography.labelSmall, color = Slate400)
                                            Text(signupExam, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = Slate100)
                                        }
                                    }
                                    Icon(Icons.Default.ArrowDropDown, "Choose", tint = Slate400)
                                }
                            }

                            OutlinedTextField(
                                value = signupPassword,
                                onValueChange = { signupPassword = it },
                                modifier = Modifier.fillMaxWidth(),
                                label = { Text("Password (min 6 chars)") },
                                placeholder = { Text("Create secure password") },
                                leadingIcon = { Icon(Icons.Default.Lock, "Lock", tint = Slate400) },
                                singleLine = true,
                                visualTransformation = if (showSignupPassword) VisualTransformation.None else PasswordVisualTransformation(),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                                trailingIcon = {
                                    IconButton(onClick = { showSignupPassword = !showSignupPassword }) {
                                        Icon(
                                            if (showSignupPassword) Icons.Default.VisibilityOff else Icons.Default.Visibility,
                                            "Toggle visibility",
                                            tint = Slate400
                                        )
                                    }
                                },
                                shape = RoundedCornerShape(14.dp),
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = Amber500,
                                    unfocusedBorderColor = Slate700,
                                    focusedContainerColor = Slate950,
                                    unfocusedContainerColor = Slate950
                                )
                            )

                            Button(
                                onClick = { onSignup(signupName, signupEmail, signupExam, signupPassword) },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(48.dp),
                                enabled = !isLoading,
                                shape = RoundedCornerShape(14.dp),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = Amber500,
                                    contentColor = Slate950
                                )
                            ) {
                                if (isLoading) {
                                    CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp, color = Slate950)
                                } else {
                                    Text("Create Aspirant Account →", fontWeight = FontWeight.ExtraBold, fontSize = 14.sp)
                                }
                            }
                        }
                    }
                }
            }

            // Trust Footer
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(Icons.Default.Shield, contentDescription = null, tint = Emerald500, modifier = Modifier.size(16.dp))
                Text(
                    text = "Strict Data Isolation • On-Device Encrypted Storage",
                    style = MaterialTheme.typography.labelSmall,
                    color = Slate400
                )
            }
        }
    }

    // Exam Picker Dialog
    if (showExamPicker) {
        AlertDialog(
            onDismissRequest = { showExamPicker = false },
            title = { Text("Select Target Examination", fontWeight = FontWeight.Bold, color = Slate100) },
            containerColor = Slate900,
            text = {
                Column(
                    modifier = Modifier.verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    EXAM_OPTIONS.forEach { exam ->
                        val selected = exam == signupExam
                        Surface(
                            onClick = {
                                signupExam = exam
                                showExamPicker = false
                            },
                            modifier = Modifier.fillMaxWidth(),
                            color = if (selected) Amber500.copy(alpha = 0.2f) else Slate950,
                            shape = RoundedCornerShape(10.dp),
                            border = androidx.compose.foundation.BorderStroke(
                                1.dp,
                                if (selected) Amber500 else Slate800
                            )
                        ) {
                            Row(
                                modifier = Modifier.padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                RadioButton(
                                    selected = selected,
                                    onClick = null,
                                    colors = RadioButtonDefaults.colors(selectedColor = Amber500)
                                )
                                Spacer(Modifier.width(8.dp))
                                Text(
                                    text = exam,
                                    style = MaterialTheme.typography.bodyMedium,
                                    fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
                                    color = if (selected) Amber400 else Slate100
                                )
                            }
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showExamPicker = false }) {
                    Text("Close", color = Amber400)
                }
            }
        )
    }
}
