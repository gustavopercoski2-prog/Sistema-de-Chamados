package com.chamados.auth_api.controller;

import com.chamados.auth_api.dto.LoginRequest;
import com.chamados.auth_api.dto.LoginResponse;
import com.chamados.auth_api.repository.UserRepository;
import com.chamados.auth_api.model.User;
import com.chamados.auth_api.utils.DjangoPasswordHasher;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@RestController
@RequestMapping("/auth")
@CrossOrigin(origins = "*") // api acessada fora do dominio
public class AuthController {

    @Autowired
    private UserRepository repository;

    // valida hash do django
    private final DjangoPasswordHasher hasher = new DjangoPasswordHasher();

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest body) {
        Optional<User> user = repository.findByUsername(body.username());

        if (user.isEmpty()) {
            return ResponseEntity.status(401).body("usuario nao encontrado");
        }

        boolean senhaValida = hasher.checkPassword(
            body.password(),
            user.get().getPassword()
        );

        if (!senhaValida) {
            return ResponseEntity.status(401).body("senha invalida");
        }

        // mock de token (integracao futura)
        return ResponseEntity.ok(new LoginResponse("token-validado-com-sucesso"));
    }
}
